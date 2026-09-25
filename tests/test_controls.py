import sqlite3
import tempfile
import unittest
from pathlib import Path
from etl.mock_erp_adapter import apply_batch
from validation.publication import enforce_controls, validate_contract

class ControlTests(unittest.TestCase):
    def test_only_expected_synthetic_failure_is_allowed(self):
        row=dict(TestName='Negative ending on-hand',Status='FAIL')
        enforce_controls([row],synthetic=True)
        self.assertEqual(row['Severity'],'EXPECTED_SCENARIO')
        with self.assertRaises(ValueError): enforce_controls([row],synthetic=False)
        with self.assertRaises(ValueError): enforce_controls([dict(TestName='Orphan invoice lines',Status='FAIL')])
        with self.assertRaises(ValueError): enforce_controls([])

    def test_schema_rejects_unresolved_keys(self):
        with sqlite3.connect(':memory:') as db:
            db.executescript(Path('sql/sqlite/warehouse.sql').read_text())
            with self.assertRaises(sqlite3.IntegrityError): db.execute("INSERT INTO FactInventory VALUES ('x','missing','missing','2025-01-01',1)")

    def test_mock_replay_late_arrival_reversal_delete_and_conflict(self):
        e=dict(source='mock',legal_entity='US01',invoice_id='INV1',line=1,version=1,revenue_cents=12345,currency='USD',uom='EA',operation='upsert')
        with sqlite3.connect(':memory:') as db:
            self.assertEqual(apply_batch(db,[e,e]),12345)
            self.assertEqual(apply_batch(db,[dict(e,version=3,revenue_cents=-100)]),-100)
            self.assertEqual(apply_batch(db,[dict(e,version=2)]),-100)
            with self.assertRaises(ValueError): apply_batch(db,[dict(e,version=3,revenue_cents=100)])
            self.assertEqual(apply_batch(db,[dict(e,version=4,operation='delete')]),0)
            with self.assertRaises(ValueError): apply_batch(db,[dict(e,currency='EUR')])

    def test_candidate_failure_keeps_last_good_file(self):
        from etl.run_pipeline import run
        from unittest.mock import patch
        import pandas as pd
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);web=root/'web';web.mkdir();(web/'dashboard.json').write_text('last-good')
            with patch('etl.run_pipeline.validate',return_value=pd.DataFrame([dict(TestName='Duplicate InvoiceID',Status='FAIL')])):
                with self.assertRaises(ValueError):run(False,raw_dir=root/'raw',processed_dir=root/'processed',web_dir=web)
            self.assertEqual((web/'dashboard.json').read_text(),'last-good')

    def test_reconciliation_fails_closed(self):
        with self.assertRaises(ValueError): validate_contract({'executive_kpis':{}})

if __name__=='__main__': unittest.main()
