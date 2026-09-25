"""Normalize raw CSV fields without overwriting the original landing files."""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

from utils.config import PROCESSED_DIR, RAW_DIR

DATE_COLUMNS = {"InvoiceHeader": ["InvoiceDate"], "SalesOrderHeader": ["OrderDate", "RequestedShipDate", "ActualShipDate", "OrderCreatedTimestamp"], "PurchaseOrderHeader": ["CreatedDate", "ExpectedDeliveryDate"], "InventoryTransaction": ["TransactionDate"], "CustomerReturn": ["ReturnDate"]}

def clean_file(path: Path, output: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    for col in frame.select_dtypes(include="object"):
        frame[col] = frame[col].astype("string").str.strip().replace({"": pd.NA})
    for col in DATE_COLUMNS.get(path.stem, []):
        if col in frame: frame[col] = pd.to_datetime(frame[col], errors="coerce")
    # Preserve all rows; the orchestrator validates before this normalization step. No quarantine service is implemented.
    frame.to_csv(output / path.name, index=False, date_format="%Y-%m-%d")
    return frame

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("--input",type=Path,default=RAW_DIR); parser.add_argument("--output",type=Path,default=PROCESSED_DIR); args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    for path in sorted(args.input.glob("*.csv")): clean_file(path,args.output)
    print(f"Normalized CSVs written to {args.output}")

if __name__ == "__main__": main()

