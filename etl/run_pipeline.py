"""Run the local synthetic ERP-to-static-dashboard pipeline in dependency order."""
from __future__ import annotations
import argparse
from pathlib import Path

from etl.clean_data import clean_file
from etl.build_analytics import build
from etl.export_dashboard_data import export
from python.generators.generate_all import build_transactions
from python.generators.generate_master_data import create_master_data
from utils.config import NUM_PURCHASE_ORDERS, NUM_SALES_ORDERS, PROCESSED_DIR, RAW_DIR
from utils.helpers import write_csv
from validation.run_data_quality_checks import validate
from validation.reconciliation import reconcile

def run(generate: bool=True, orders: int=NUM_SALES_ORDERS, purchase_orders: int=NUM_PURCHASE_ORDERS) -> None:
    if generate:
        RAW_DIR.mkdir(parents=True,exist_ok=True)
        masters=create_master_data()
        for name,frame in {**masters,**build_transactions(masters,orders,purchase_orders)}.items(): write_csv(frame,RAW_DIR/f"{name}.csv")
    PROCESSED_DIR.mkdir(parents=True,exist_ok=True)
    for source in RAW_DIR.glob("*.csv"): clean_file(source,PROCESSED_DIR)
    build()
    write_csv(validate(),PROCESSED_DIR/"data_quality.csv")
    export()
    write_csv(reconcile(),PROCESSED_DIR/"reconciliation.csv")
    export()  # Include the just-computed reconciliation in the final dashboard contract.
    print("Pipeline complete. See web/data/dashboard.json and data/processed/.")

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orders",type=int,default=NUM_SALES_ORDERS)
    parser.add_argument("--purchase-orders",type=int,default=NUM_PURCHASE_ORDERS)
    parser.add_argument("--skip-generation",action="store_true",help="Reuse existing data/raw CSV extracts")
    args=parser.parse_args()
    run(not args.skip_generation,args.orders,args.purchase_orders)

if __name__=="__main__": main()
