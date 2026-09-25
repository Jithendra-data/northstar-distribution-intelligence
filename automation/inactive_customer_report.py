"""List valuable customers with no recent invoiced purchase."""
import pandas as pd
from utils.config import RAW_DIR, PROCESSED_DIR
from utils.helpers import write_csv

def run(source=RAW_DIR, revenue_threshold=25000, inactive_days=60, as_of=None):
    invoices=pd.read_csv(source/"InvoiceHeader.csv",parse_dates=["InvoiceDate"])
    lines=pd.read_csv(source/"InvoiceLine.csv")
    customers=pd.read_csv(source/"Customer.csv")
    reps=pd.read_csv(source/"SalesRep.csv")
    facts=lines.merge(invoices[["InvoiceID","CustomerID","InvoiceDate"]],on="InvoiceID")
    x=facts.groupby("CustomerID",as_index=False).agg(LifetimeRevenue=("Revenue","sum"),LastPurchaseDate=("InvoiceDate","max"),PurchaseFrequency=("InvoiceID","nunique"))
    x=x.merge(customers[["CustomerID","CustomerName","SalesRepID"]],on="CustomerID").merge(reps[["SalesRepID","SalesRepName"]],on="SalesRepID",how="left")
    today=pd.Timestamp(as_of or invoices.InvoiceDate.max()); x["DaysInactive"]=(today-pd.to_datetime(x.LastPurchaseDate)).dt.days
    return x[(x.LifetimeRevenue>=revenue_threshold)&(x.DaysInactive>inactive_days)].sort_values("LifetimeRevenue",ascending=False)

if __name__=="__main__":
    result=run(); write_csv(result,PROCESSED_DIR/"inactive_customer_report.csv"); print(f"Found {len(result)} valuable inactive customers")

