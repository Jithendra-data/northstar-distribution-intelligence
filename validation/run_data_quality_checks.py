"""Run cross-file quality checks and write machine-readable results."""
from __future__ import annotations
import argparse
from datetime import date
from pathlib import Path
import pandas as pd
from utils.config import RAW_DIR
from utils.helpers import write_csv

def validate(source: Path=RAW_DIR) -> pd.DataFrame:
    def read(name): return pd.read_csv(source/f"{name}.csv")
    checks=[]
    def add(name, frame, failures, domain):
        checked=len(frame); failed=int(failures.sum()) if hasattr(failures,"sum") else int(failures)
        checks.append({"TestName":name,"Domain":domain,"RecordsChecked":checked,"FailedRecords":failed,"PassedRecords":checked-failed,"PassRate":(checked-failed)/checked if checked else 1.0,"Status":"PASS" if failed==0 else "FAIL","RunDate":date.today().isoformat()})
    for name,key in [("InvoiceHeader","InvoiceID"),("SalesOrderHeader","SalesOrderID"),("PurchaseOrderHeader","PONumber")]:
        f=read(name); add(f"Duplicate {key}",f,f[key].duplicated(keep=False),"Transactions")
    ih,il=read("InvoiceHeader"),read("InvoiceLine")
    add("Orphan invoice lines",il,~il.InvoiceID.isin(ih.InvoiceID),"Sales")
    sh,sl=read("SalesOrderHeader"),read("SalesOrderLine")
    add("Invoices without sales orders",ih,~ih.SalesOrderID.isin(sh.SalesOrderID),"Sales")
    add("Orphan order lines",sl,~sl.SalesOrderID.isin(sh.SalesOrderID),"Sales")
    c,p,v,w=read("Customer"),read("Product"),read("Vendor"),read("Warehouse")
    add("Missing invoice customers",ih,~ih.CustomerID.isin(c.CustomerID),"Sales")
    add("Missing invoice products",il,~il.ProductID.isin(p.ProductID),"Sales")
    pol,poh=read("PurchaseOrderLine"),read("PurchaseOrderHeader")
    add("Duplicate PO lines",pol,pol.duplicated(["PONumber","LineNumber"],keep=False),"Purchasing")
    add("Missing PO vendors",poh,~poh.VendorID.isin(v.VendorID),"Purchasing")
    add("PO received above ordered",pol,pol.ReceivedQuantity>pol.OrderedQuantity,"Purchasing")
    add("Negative invoice quantity",il,il.Quantity<0,"Sales")
    add("Missing or nonpositive product cost",p,p.UnitCost.isna()|(p.UnitCost<=0),"Product")
    for table,columns in [("InvoiceHeader",["InvoiceDate"]),("SalesOrderHeader",["OrderDate"]),("PurchaseOrderHeader",["CreatedDate","ExpectedDeliveryDate"]),("InventoryTransaction",["TransactionDate"]),("CustomerReturn",["ReturnDate"])]:
        f=read(table)
        if len(f):
            invalid=pd.Series(False,index=f.index)
            for column in columns:
                if column in f: invalid |= pd.to_datetime(f[column],errors="coerce").isna()
            add(f"Invalid {table} dates",f,invalid,"Dates")
    tx=read("InventoryTransaction")
    if len(tx):
        add("Invalid inventory warehouse",tx,~tx.WarehouseID.isin(w.WarehouseID),"Inventory")
        balances=tx.groupby(["ProductID","WarehouseID"],as_index=False).Quantity.sum().rename(columns={"Quantity":"EndingOnHand"})
        add("Negative ending on-hand",balances,balances.EndingOnHand<0,"Inventory")
    return pd.DataFrame(checks)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--input",type=Path,default=RAW_DIR); parser.add_argument("--output",type=Path,default=Path("data/processed/data_quality.csv")); args=parser.parse_args()
    result=validate(args.input); write_csv(result,args.output); print(result.to_string(index=False))

if __name__=="__main__": main()
