"""List open purchase commitments past expected receipt date."""
import pandas as pd
from utils.config import RAW_DIR, PROCESSED_DIR
from utils.helpers import write_csv

def run(source=RAW_DIR, as_of=None):
    today=pd.Timestamp(as_of or pd.Timestamp.today().normalize())
    h=pd.read_csv(source/"PurchaseOrderHeader.csv",parse_dates=["CreatedDate","ExpectedDeliveryDate"])
    l=pd.read_csv(source/"PurchaseOrderLine.csv")
    vendors=pd.read_csv(source/"Vendor.csv")
    x=h.merge(l,on="PONumber").merge(vendors[["VendorID","VendorName"]],on="VendorID",how="left")
    x=x[(x.ExpectedDeliveryDate<today)&(x.RemainingQuantity>0)].copy()
    x["DaysLate"]=(today-x.ExpectedDeliveryDate).dt.days;x["RemainingValue"]=x.RemainingQuantity*x.UnitCost
    return x[["PONumber","VendorName","CreatedDate","ExpectedDeliveryDate","DaysLate","RemainingQuantity","RemainingValue"]]

if __name__=="__main__":
    result=run(); write_csv(result,PROCESSED_DIR/"overdue_po_report.csv"); print(f"Found {len(result)} overdue PO lines")

