"""Build compact analytical summaries from raw synthetic ERP extracts."""
from __future__ import annotations

from pathlib import Path
import pandas as pd

from utils.config import RAW_DIR, PROCESSED_DIR
from utils.helpers import write_csv

def build(input_dir: Path=PROCESSED_DIR, output_dir: Path=PROCESSED_DIR, warehouse: Path|None=None) -> dict[str,pd.DataFrame]:
    invoices=pd.read_csv(input_dir/"InvoiceLine.csv")
    ih=pd.read_csv(input_dir/"InvoiceHeader.csv",parse_dates=["InvoiceDate"])
    sales=invoices.merge(ih[["InvoiceID","InvoiceDate","CustomerID"]],on="InvoiceID",how="inner")
    sales["YearMonth"]=sales.InvoiceDate.dt.to_period("M").astype(str)
    monthly=sales.groupby("YearMonth",as_index=False).agg(Revenue=("Revenue","sum"),GrossProfit=("GrossProfit","sum"),Units=("Quantity","sum"),Invoices=("InvoiceID","nunique"))
    if warehouse is not None:
        import sqlite3
        with sqlite3.connect(warehouse) as db: monthly=pd.read_sql_query("SELECT * FROM MonthlySales ORDER BY YearMonth",db)
        db.close()
    monthly["GrossMarginPct"]=monthly.GrossProfit.div(monthly.Revenue.where(monthly.Revenue.ne(0)))
    dimc=pd.read_csv(input_dir/"Customer.csv")
    customer=sales.groupby("CustomerID",as_index=False).agg(LifetimeRevenue=("Revenue","sum"),GrossProfit=("GrossProfit","sum"),LastPurchaseDate=("InvoiceDate","max"),Orders=("InvoiceID","nunique"))
    customer=customer.merge(dimc[["CustomerID","CustomerName","CustomerGroup","Region","SalesRepID"]],on="CustomerID",how="left")
    customer["DaysInactive"]=(sales.InvoiceDate.max()-pd.to_datetime(customer.LastPurchaseDate)).dt.days
    customer["Segment"]=customer.DaysInactive.map(lambda d:"Lost" if d>180 else "At Risk" if d>90 else "Active")
    products=pd.read_csv(input_dir/"Product.csv")
    product=sales.groupby("ProductID",as_index=False).agg(Revenue=("Revenue","sum"),Units=("Quantity","sum"),GrossProfit=("GrossProfit","sum"))
    product=product.merge(products[["ProductID","SKU","ProductName","CategoryName","VendorID","UnitCost"]],on="ProductID",how="right").fillna({"Revenue":0,"Units":0,"GrossProfit":0})
    po=pd.read_csv(input_dir/"PurchaseOrderLine.csv").merge(pd.read_csv(input_dir/"PurchaseOrderHeader.csv"),on="PONumber",how="left")
    vendor=po.groupby("VendorID",as_index=False).agg(POCount=("PONumber","nunique"),OrderedQuantity=("OrderedQuantity","sum"),ReceivedQuantity=("ReceivedQuantity","sum"),POValue=("LineAmount","sum"))
    vendor["FillRate"]=vendor.ReceivedQuantity.div(vendor.OrderedQuantity.where(vendor.OrderedQuantity.ne(0)))
    result={"monthly_sales":monthly,"customer_performance":customer,"product_performance":product,"vendor_performance":vendor}
    output_dir.mkdir(parents=True,exist_ok=True)
    for name,frame in result.items(): write_csv(frame,output_dir/f"{name}.csv")
    return result

if __name__=="__main__": build()

