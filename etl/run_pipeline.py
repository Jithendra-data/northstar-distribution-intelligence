"""Build a candidate, validate it, then atomically replace the public contract."""
import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import time
import tracemalloc
from pathlib import Path
import pandas as pd
from etl.clean_data import clean_file
from etl.build_analytics import build
from etl.export_dashboard_data import export
from etl.warehouse import load_warehouse
from python.generators.generate_all import build_transactions
from python.generators.generate_master_data import create_master_data
from utils.config import NUM_PURCHASE_ORDERS, NUM_SALES_ORDERS, PROCESSED_DIR, RAW_DIR, WEB_DATA_DIR
from utils.helpers import write_csv, write_json
from validation.run_data_quality_checks import validate
from validation.reconciliation import reconcile
from validation.publication import enforce_controls, validate_contract

def run(generate=True, orders=NUM_SALES_ORDERS, purchase_orders=NUM_PURCHASE_ORDERS, raw_dir=RAW_DIR, processed_dir=PROCESSED_DIR, web_dir=WEB_DATA_DIR):
    started=time.perf_counter();timings={}
    raw_dir.mkdir(parents=True,exist_ok=True);processed_dir.mkdir(parents=True,exist_ok=True)
    if generate:
        masters=create_master_data()
        for name,frame in {**masters,**build_transactions(masters,orders,purchase_orders)}.items(): write_csv(frame,raw_dir/f'{name}.csv')
    timings['generation_seconds']=round(time.perf_counter()-started,3);checkpoint=time.perf_counter();tracemalloc.start()
    checks=validate(raw_dir).to_dict(orient='records')
    enforce_controls(checks,synthetic=True)
    write_csv(pd.DataFrame(checks),processed_dir/'data_quality.csv')
    for source in raw_dir.glob('*.csv'): clean_file(source,processed_dir)
    warehouse=processed_dir/'warehouse.sqlite'
    counts=load_warehouse(processed_dir,warehouse)
    data=build(processed_dir,processed_dir,warehouse)
    timings['validation_model_seconds']=round(time.perf_counter()-checkpoint,3);checkpoint=time.perf_counter()
    payload=export(data,source=processed_dir,write=False)
    if not generate: payload['pipeline_metadata']['random_seed']=None
    payload['pipeline_metadata']['generation_mode']='generated' if generate else 'reused raw files; seed unknown'
    payload['data_quality']['results']=checks
    rec=reconcile(raw_dir,warehouse,payload);payload['reconciliation']=rec.to_dict(orient='records')
    validate_contract(payload);write_csv(rec,processed_dir/'reconciliation.csv')
    manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(raw_dir.glob('*.csv'))}
    _,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    timings['export_reconcile_seconds']=round(time.perf_counter()-checkpoint,3);timings['total_seconds']=round(time.perf_counter()-started,3)
    payload['pipeline_metadata'].update(publication_status='APPROVED',expected_exceptions=[r['TestName'] for r in checks if r['Status']!='PASS'],warehouse_engine='SQLite',warehouse_rows=counts,timings=timings,peak_python_allocations_mb=round(peak/1024**2,2),python_version=platform.python_version(),dependencies={p:importlib.metadata.version(p) for p in ['pandas','numpy','Faker']},input_sha256=manifest,commit=os.getenv('GITHUB_SHA','local'),workflow_run=os.getenv('GITHUB_RUN_ID','local'))
    web_dir.mkdir(parents=True,exist_ok=True)
    candidate=web_dir/'dashboard.candidate.json';write_json(payload,candidate)
    validate_contract(json.loads(candidate.read_text(encoding='utf-8')))
    candidate.replace(web_dir/'dashboard.json')
    evidence={**payload['pipeline_metadata'],'published_bytes':(web_dir/'dashboard.json').stat().st_size,'published_sha256':hashlib.sha256((web_dir/'dashboard.json').read_bytes()).hexdigest()}
    write_json(evidence,processed_dir/'run_manifest.json')
    print(f'APPROVED: {counts}; {timings}')
    return payload

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--orders',type=int,default=NUM_SALES_ORDERS);parser.add_argument('--purchase-orders',type=int,default=NUM_PURCHASE_ORDERS)
    parser.add_argument('--skip-generation',action='store_true');parser.add_argument('--workspace',type=Path,help='Isolate test files')
    args=parser.parse_args();kwargs={} if args.workspace is None else dict(raw_dir=args.workspace/'raw',processed_dir=args.workspace/'processed',web_dir=args.workspace/'web')
    run(not args.skip_generation,args.orders,args.purchase_orders,**kwargs)
