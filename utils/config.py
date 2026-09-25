"""Central project configuration. Paths are resolved from the repository root."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
WEB_DATA_DIR = ROOT / "web" / "data"
NUM_CUSTOMERS = 5_000
NUM_PRODUCTS = 2_000
NUM_VENDORS = 150
NUM_SALES_REPS = 25
NUM_SALES_ORDERS = 75_000
NUM_PURCHASE_ORDERS = 10_000
START_DATE = "2023-01-01"
END_DATE = "2025-12-31"
RANDOM_SEED = 73_041

