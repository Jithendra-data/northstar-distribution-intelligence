"""Create reproducible, wholly fictional NorthStar master records."""
from __future__ import annotations

import numpy as np
import pandas as pd
from faker import Faker

from utils.config import NUM_CUSTOMERS, NUM_PRODUCTS, NUM_SALES_REPS, NUM_VENDORS, RANDOM_SEED

CATEGORIES = ["Beverages", "Snacks", "Cleaning", "Paper", "Personal Care", "Food Storage", "Kitchen", "Seasonal", "Pet Care", "Health", "Office", "Safety", "Lighting", "Hardware", "Automotive", "Outdoor", "Electrical", "Packaging", "Appliances", "Linen"]
GROUPS = ["Independent Retail", "Regional Chain", "National Chain", "Distributor", "Key Account", "Specialty Retail", "Convenience", "Online"]
STATES = ["CO", "TX", "IL", "GA", "AZ", "CA", "MO", "NC", "TN", "UT", "OH", "PA"]
CITY_STATE = {"CO": "Denver", "TX": "Dallas", "IL": "Chicago", "GA": "Atlanta", "AZ": "Phoenix", "CA": "Sacramento", "MO": "St. Louis", "NC": "Charlotte", "TN": "Nashville", "UT": "Salt Lake City", "OH": "Columbus", "PA": "Pittsburgh"}


def create_master_data() -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(RANDOM_SEED)
    fake = Faker(); Faker.seed(RANDOM_SEED)
    warehouses = pd.DataFrame([
        ("DEN", "Denver Distribution Center", "Denver", "CO"), ("DAL", "Dallas Distribution Center", "Dallas", "TX"),
        ("CHI", "Chicago Distribution Center", "Chicago", "IL"), ("ATL", "Atlanta Distribution Center", "Atlanta", "GA")
    ], columns=["WarehouseID", "WarehouseName", "City", "State"])
    reps = pd.DataFrame([{"SalesRepID": f"SR{i:03}", "SalesRepName": fake.name(), "Region": ["West", "South", "Midwest", "East"][i % 4], "Territory": f"Territory {i:02}", "HireDate": fake.date_between("-12y", "-1y"), "Status": "Active"} for i in range(1, NUM_SALES_REPS + 1)])
    vendors = []
    for i in range(1, NUM_VENDORS + 1):
        state = STATES[(i - 1) % len(STATES)]
        vendors.append({"VendorID": f"V{i:04}", "VendorName": f"{fake.company()} Supply", "City": CITY_STATE[state], "State": state, "PaymentTerms": rng.choice(["Net 30", "Net 45", "2/10 Net 30"]), "StandardLeadTimeDays": 8 if i == 1 else int(rng.integers(5, 15)), "Status": "Active"})
    vendors = pd.DataFrame(vendors)
    customers = []
    for i in range(1, NUM_CUSTOMERS + 1):
        state = STATES[int(rng.integers(0, len(STATES)))]
        customers.append({"CustomerID": f"C{i:05}", "CustomerName": fake.company(), "CustomerGroup": rng.choice(GROUPS, p=[.28,.16,.07,.08,.08,.12,.12,.09]), "AddressLine1": fake.street_address(), "City": CITY_STATE[state], "State": state, "ZipCode": fake.postcode(), "Region": "West" if state in ["CO","AZ","CA","UT"] else "South" if state in ["TX","GA","NC","TN"] else "Midwest" if state in ["IL","MO","OH"] else "East", "SalesRepID": f"SR{int(rng.integers(1, NUM_SALES_REPS + 1)):03}", "CreditLimit": int(rng.choice([10000,25000,50000,100000,250000])), "PaymentTerms": rng.choice(["Net 30", "Net 45", "Net 60"]), "CreatedDate": fake.date_between("-8y", "-1y"), "Status": "Active"})
    customers = pd.DataFrame(customers)
    products = []
    category_cost = rng.uniform(4, 48, len(CATEGORIES))
    for i in range(1, NUM_PRODUCTS + 1):
        cat_idx = (i - 1) % len(CATEGORIES)
        cost = round(float(category_cost[cat_idx] * rng.uniform(.55, 1.65)), 2)
        products.append({"ProductID": f"P{i:05}", "SKU": f"NS-{i:05}", "ProductName": f"{fake.color_name()} {CATEGORIES[cat_idx]} {fake.word().title()}", "BrandID": f"B{(i-1)%100+1:03}", "CategoryID": f"CAT{cat_idx+1:02}", "CategoryName": CATEGORIES[cat_idx], "VendorID": f"V{1 if i % 35 == 0 else int(rng.integers(1, NUM_VENDORS + 1)):04}", "UnitCost": cost, "StandardPrice": round(cost / float(rng.uniform(.48, .72)), 2), "PackSize": int(rng.choice([1, 2, 4, 6, 12, 24])), "LaunchDate": fake.date_between("-6y", "-6m"), "DiscontinuedFlag": bool(i % 97 == 0), "Status": "Active"})
    return {"Warehouse": warehouses, "SalesRep": reps, "Vendor": vendors, "Customer": customers, "Product": pd.DataFrame(products)}

