"""Tested invoice change contract; no connection to a real ERP is claimed."""
import sqlite3

def apply_batch(db: sqlite3.Connection, events: list[dict]):
    db.execute('CREATE TABLE IF NOT EXISTS invoice_changes (source TEXT, entity TEXT, invoice TEXT, line INTEGER, version INTEGER, revenue_cents INTEGER, deleted INTEGER, PRIMARY KEY(source,entity,invoice,line))')
    with db:
        for e in events:
            if e.get('currency')!='USD' or e.get('uom')!='EA': raise ValueError('Unsupported currency or unit: normalize before ingestion')
            if e.get('operation') not in ['upsert','delete']: raise ValueError('Unsupported operation')
            if not isinstance(e.get('revenue_cents'),int) or not isinstance(e.get('version'),int): raise ValueError('Integer money and monotonically increasing versions required')
            row=(e['source'],e['legal_entity'],e['invoice_id'],e['line'],e['version'],e['revenue_cents'],int(e['operation']=='delete'))
            old=db.execute('SELECT version,revenue_cents,deleted FROM invoice_changes WHERE source=? AND entity=? AND invoice=? AND line=?',row[:4]).fetchone()
            if old and old[0]==e['version'] and old[1:]!=row[5:]: raise ValueError('Conflicting payload at same version')
            db.execute('INSERT INTO invoice_changes VALUES (?,?,?,?,?,?,?) ON CONFLICT(source,entity,invoice,line) DO UPDATE SET version=excluded.version,revenue_cents=excluded.revenue_cents,deleted=excluded.deleted WHERE excluded.version>invoice_changes.version',row)
    return db.execute('SELECT COALESCE(SUM(revenue_cents),0) FROM invoice_changes WHERE deleted=0').fetchone()[0]
