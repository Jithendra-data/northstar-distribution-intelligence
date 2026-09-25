"""Independent source to executed SQLite warehouse to published KPI reconciliation."""
from pathlib import Path
import sqlite3
import pandas as pd

def reconcile(source: Path, warehouse: Path, payload: dict) -> pd.DataFrame:
    raw=pd.read_csv(source/'InvoiceLine.csv')
    balances=pd.read_csv(source/'InventoryTransaction.csv').groupby('ProductID').Quantity.sum()
    cost=pd.read_csv(source/'Product.csv').set_index('ProductID').UnitCost
    po=pd.read_csv(source/'PurchaseOrderLine.csv')
    specs=[('Revenue',raw.Revenue.sum(),'SELECT SUM(Revenue) FROM FactSales','revenue','USD'),
      ('GrossProfit',raw.GrossProfit.sum(),'SELECT SUM(GrossProfit) FROM FactSales','gross_profit','USD'),
      ('Units',raw.Quantity.sum(),'SELECT SUM(Quantity) FROM FactSales','units','units'),
      ('EndingInventoryValue',(balances*cost).sum(),'SELECT SUM(f.Quantity*p.UnitCost) FROM FactInventory f JOIN DimProduct p USING(ProductID)','inventory_value','USD'),
      ('OpenPOValue',(po.RemainingQuantity*po.UnitCost).sum(),'SELECT SUM(RemainingQuantity*UnitCost) FROM FactPurchasing','open_po_value','USD')]
    rows=[]
    with sqlite3.connect(warehouse) as db:
        for name,raw_value,sql,key,unit in specs:
            fact=float(db.execute(sql).fetchone()[0] or 0);published=float(payload['executive_kpis'][key]);raw_value=float(raw_value)
            fv=abs(raw_value-fact);dv=abs(raw_value-published);tolerance=0.000001 if unit=='units' else 0.01
            rows.append(dict(Measure=name,RawValue=raw_value,FactValue=fact,DashboardValue=published,Variance=dv,SourceToWarehouseVariance=fv,SourceToDashboardVariance=dv,Unit=unit,Tolerance=tolerance,Status='PASS' if fv<=tolerance and dv<=tolerance else 'FAIL',Provenance='Raw CSV / SQLite fact query / candidate JSON'))
    db.close()
    return pd.DataFrame(rows)
