"""Isolated integration run; never overwrite the public data during CI tests."""
import json
import sqlite3
import tempfile
from pathlib import Path
from etl.run_pipeline import run
from validation.publication import validate_contract

with tempfile.TemporaryDirectory() as temp:
    root=Path(temp)
    kwargs=dict(raw_dir=root/'raw',processed_dir=root/'processed',web_dir=root/'web')
    first=run(True,1000,250,**kwargs)
    validate_contract(first)
    second=run(False,**kwargs)
    assert first['executive_kpis']==second['executive_kpis'],'Full rebuild must be idempotent for the same source files'
    with sqlite3.connect(root/'processed/warehouse.sqlite') as db:
        assert not db.execute('PRAGMA foreign_key_check').fetchall()
    db.close()
    print('PASS: isolated generation, staging, all four facts, reconciliation, publication, repeat rebuild')
