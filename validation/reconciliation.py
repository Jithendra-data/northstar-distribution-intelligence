"""Reconcile additive invoice measures from raw invoice lines to the curated extract."""
from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
from utils.config import RAW_DIR, PROCESSED_DIR
from utils.helpers import write_csv

def reconcile(source: Path=RAW_DIR) -> pd.DataFrame:
    raw=pd.read_csv(source/"InvoiceLine.csv")
    mart_path=PROCESSED_DIR/"monthly_sales.csv"
    dashboard_path=Path("web/data/dashboard.json")
    mart=pd.read_csv(mart_path) if mart_path.exists() else None
    dashboard=json.loads(dashboard_path.read_text(encoding="utf-8")) if dashboard_path.exists() else None
    measures={"Revenue":("Revenue","Revenue","revenue"),"GrossProfit":("GrossProfit","GrossProfit","gross_profit"),"Units":("Quantity","Units","units")}
    rows=[]
    for label,(raw_column,mart_column,dash_key) in measures.items():
        raw_total=float(raw[raw_column].sum())
        fact_total=float(mart[mart_column].sum()) if mart is not None and mart_column in mart else None
        dash_total=float(dashboard["executive_kpis"].get(dash_key,0)) if dashboard is not None and dash_key in dashboard.get("executive_kpis",{}) else None
        variance=abs(raw_total-fact_total) if fact_total is not None else None
        rows.append({"Measure":label,"RawValue":raw_total,"FactValue":fact_total,"DashboardValue":dash_total,"Variance":variance,"Status":"NOT RUN" if fact_total is None or dash_total is None else "PASS" if abs(raw_total-fact_total)<0.01 and abs(raw_total-dash_total)<0.01 else "FAIL"})
    tx=pd.read_csv(source/"InventoryTransaction.csv")
    balances=tx.groupby(["ProductID","WarehouseID"],as_index=False).Quantity.sum()
    product_cost=pd.read_csv(source/"Product.csv")[["ProductID","UnitCost"]]
    inventory_value=float(balances.merge(product_cost,on="ProductID").eval("Quantity * UnitCost").sum())
    po=pd.read_csv(source/"PurchaseOrderLine.csv")
    open_po_value=float((po.RemainingQuantity*po.UnitCost).sum())
    if dashboard is not None:
        for label,value,key in [("EndingInventoryValue",inventory_value,"inventory_value"),("OpenPOValue",open_po_value,"open_po_value")]:
            dash_total=dashboard.get("executive_kpis",{}).get(key)
            variance=abs(value-dash_total) if dash_total is not None else None
            rows.append({"Measure":label,"RawValue":value,"FactValue":value,"DashboardValue":dash_total,"Variance":variance,"Status":"NOT RUN" if dash_total is None else "PASS" if variance<0.01 else "FAIL"})
    return pd.DataFrame(rows)

def main():
    out=reconcile(); write_csv(out,PROCESSED_DIR/"reconciliation.csv"); print(out.to_string(index=False))

if __name__=="__main__": main()
