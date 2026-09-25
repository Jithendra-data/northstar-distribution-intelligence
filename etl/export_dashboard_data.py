"""Export small static JSON contracts consumed by the GitHub Pages dashboard."""
from __future__ import annotations

import pandas as pd

from etl.build_analytics import build
from utils.config import RAW_DIR, WEB_DATA_DIR, PROCESSED_DIR
from utils.helpers import write_json

def export() -> None:
    data=build()
    monthly=data["monthly_sales"].fillna(0)
    customers=data["customer_performance"].fillna(0)
    products=data["product_performance"].fillna(0)
    vendors=data["vendor_performance"].fillna(0)
    orders=pd.read_csv(RAW_DIR/"SalesOrderHeader.csv")
    inventory=pd.read_csv(RAW_DIR/"InventoryTransaction.csv",parse_dates=["TransactionDate"]) if (RAW_DIR/"InventoryTransaction.csv").exists() else pd.DataFrame()
    po_lines=pd.read_csv(RAW_DIR/"PurchaseOrderLine.csv")
    open_po_value=float((po_lines.RemainingQuantity*po_lines.UnitCost).sum())
    snapshot=pd.DataFrame()
    if not inventory.empty:
        as_of=inventory.TransactionDate.max()
        stock=inventory.groupby(["ProductID","WarehouseID"],as_index=False).agg(AvailableQty=("Quantity","sum"))
        shipments=inventory[inventory.TransactionType.eq("Sales Shipment")].copy()
        shipments["UnitsSold"]=shipments.Quantity.abs()
        last30=shipments[shipments.TransactionDate>as_of-pd.Timedelta(days=30)].groupby(["ProductID","WarehouseID"]).UnitsSold.sum().rename("Sales30Day")
        last90=shipments[shipments.TransactionDate>as_of-pd.Timedelta(days=90)].groupby(["ProductID","WarehouseID"]).UnitsSold.sum().rename("Sales90Day")
        inbound=po_lines.merge(pd.read_csv(RAW_DIR/"PurchaseOrderHeader.csv")[["PONumber","WarehouseID"]],on="PONumber").groupby(["ProductID","WarehouseID"]).RemainingQuantity.sum().rename("InboundQty")
        stock=stock.set_index(["ProductID","WarehouseID"])
        for series in [last30,last90,inbound]: stock=stock.join(series,how="left")
        stock=stock.fillna(0).reset_index()
        stock["DaysOnHand"]=stock.AvailableQty.clip(lower=0).div(stock.Sales90Day/90).replace([float("inf"),-float("inf")],pd.NA)
        stock["RiskLevel"]=stock.DaysOnHand.map(lambda d:"No Recent Sales" if pd.isna(d) else "Critical" if d<7 else "High Risk" if d<14 else "Watch" if d<30 else "Healthy" if d<=90 else "Excess")
        snapshot=stock.merge(products[["ProductID","SKU","ProductName","CategoryName","VendorID","UnitCost"]],on="ProductID",how="left")
    # Business findings are calculated from transaction facts on each export, never curated constants.
    order_headers=pd.read_csv(RAW_DIR/"SalesOrderHeader.csv",parse_dates=["OrderDate","ActualShipDate"])
    order_headers["OrderToShipDays"]=(order_headers.ActualShipDate-order_headers.OrderDate).dt.days
    warehouse_service=order_headers.dropna(subset=["OrderToShipDays"]).groupby("WarehouseID").OrderToShipDays.mean()
    po_headers=pd.read_csv(RAW_DIR/"PurchaseOrderHeader.csv",parse_dates=["CreatedDate"])
    receipts=pd.read_csv(RAW_DIR/"PurchaseReceipt.csv",parse_dates=["ReceiptDate"]).merge(po_headers[["PONumber","VendorID","CreatedDate"]],on="PONumber")
    receipts["ActualLeadDays"]=(receipts.ReceiptDate-receipts.CreatedDate).dt.days
    lead=receipts.groupby("VendorID").ActualLeadDays.mean()
    vendor_one_trend=receipts[receipts.VendorID.eq("V0001")].assign(Year=lambda f:f.CreatedDate.dt.year).groupby("Year").ActualLeadDays.mean()
    at_risk=customers[(customers.LifetimeRevenue>=25000)&(customers.DaysInactive>60)]
    dead_stock=snapshot[(snapshot.Sales90Day==0)&(snapshot.AvailableQty>0)] if not snapshot.empty else pd.DataFrame()
    invoice_lines=pd.read_csv(RAW_DIR/"InvoiceLine.csv")
    invoice_headers=pd.read_csv(RAW_DIR/"InvoiceHeader.csv",parse_dates=["InvoiceDate"])
    sales_product=invoice_lines.merge(products[["ProductID","SKU","ProductName","CategoryName"]],on="ProductID",how="left").merge(invoice_headers[["InvoiceID","InvoiceDate","CustomerID"]],on="InvoiceID",how="left")
    sales_product=sales_product.merge(customers[["CustomerID","Region","SalesRepID","CustomerGroup"]],on="CustomerID",how="left")
    sales_product=sales_product.merge(order_headers[["SalesOrderID","Channel","WarehouseID"]],on="SalesOrderID",how="left")
    sales_product["Year"]=sales_product.InvoiceDate.dt.year
    sales_product["YearMonth"]=sales_product.InvoiceDate.dt.to_period("M").astype(str)
    snacks=sales_product[sales_product.CategoryName.eq("Snacks")].groupby("Year").agg(Revenue=("Revenue","sum"),Discount=("DiscountAmount","sum"),GrossProfit=("GrossProfit","sum"))
    category_summary=sales_product.groupby("CategoryName",as_index=False).agg(Revenue=("Revenue","sum"),GrossProfit=("GrossProfit","sum"),Units=("Quantity","sum"),Discount=("DiscountAmount","sum"))
    category_summary["GrossMarginPct"]=category_summary.GrossProfit.div(category_summary.Revenue.where(category_summary.Revenue.ne(0)))
    region_summary=sales_product.groupby("Region",as_index=False).agg(Revenue=("Revenue","sum"),GrossProfit=("GrossProfit","sum"))
    region_trend=sales_product.groupby(["YearMonth","Region"],as_index=False).agg(Revenue=("Revenue","sum"),GrossProfit=("GrossProfit","sum"),Units=("Quantity","sum"),Invoices=("InvoiceID","nunique"))
    booking_region=order_headers.merge(customers[["CustomerID","Region"]],on="CustomerID",how="left")
    booking_region["YearMonth"]=booking_region.OrderDate.dt.to_period("M").astype(str)
    booking_region=booking_region.groupby(["YearMonth","Region"],as_index=False).agg(Orders=("SalesOrderID","nunique"))
    region_trend=region_trend.merge(booking_region,on=["YearMonth","Region"],how="outer").fillna(0).sort_values(["YearMonth","Region"])
    rep_summary=sales_product.groupby("SalesRepID",as_index=False).agg(Revenue=("Revenue","sum"),GrossProfit=("GrossProfit","sum"),Invoices=("InvoiceID","nunique")).merge(pd.read_csv(RAW_DIR/"SalesRep.csv")[["SalesRepID","SalesRepName","Region"]],on="SalesRepID",how="left")
    channel_summary=sales_product.groupby("Channel",as_index=False).agg(Revenue=("Revenue","sum"),Invoices=("InvoiceID","nunique"))
    customer_segments=customers.groupby("Segment",as_index=False).agg(Customers=("CustomerID","nunique"),LifetimeRevenue=("LifetimeRevenue","sum"))
    warehouse_summary=order_headers.groupby("WarehouseID").agg(AvgOrderToShipDays=("OrderToShipDays","mean"),ShippedOrders=("ActualShipDate","count"),Backorders=("OrderStatus",lambda values:int(values.eq("Backordered").sum()))).reset_index()
    po_headers_full=pd.read_csv(RAW_DIR/"PurchaseOrderHeader.csv",parse_dates=["CreatedDate","ExpectedDeliveryDate"])
    po_detail=po_headers_full.merge(po_lines,on="PONumber",how="inner").merge(pd.read_csv(RAW_DIR/"Vendor.csv")[["VendorID","VendorName"]],on="VendorID",how="left")
    po_detail["RemainingValue"]=po_detail.RemainingQuantity*po_detail.UnitCost
    po_detail["DaysLate"]=(pd.Timestamp("2025-12-31")-po_detail.ExpectedDeliveryDate).dt.days.clip(lower=0)
    open_po_detail=po_detail[po_detail.RemainingQuantity.gt(0)].sort_values(["ExpectedDeliveryDate","RemainingValue"],ascending=[True,False]).head(500)
    ret=pd.read_csv(RAW_DIR/"CustomerReturn.csv")
    ret["ReturnDate"]=pd.to_datetime(ret.ReturnDate,errors="coerce")
    ret=ret.merge(products[["ProductID","CategoryName"]],on="ProductID",how="left")
    returns_by_reason=ret.groupby("ReturnReason",as_index=False).agg(Returns=("ReturnID","count"),ReturnAmount=("ReturnAmount","sum")) if not ret.empty else pd.DataFrame(columns=["ReturnReason","Returns","ReturnAmount"])
    health_returns=float(ret.loc[(ret.CategoryName.eq("Health"))&(ret.ReturnDate.dt.year.eq(2025)),"ReturnAmount"].sum())
    health_sales=float(sales_product.loc[(sales_product.CategoryName.eq("Health"))&(sales_product.InvoiceDate.dt.year.eq(2025)),"Revenue"].sum())
    findings={"warehouse_average_ship_days":{k:round(float(v),2) for k,v in warehouse_service.items()},"vendor_one_average_actual_lead_days_by_year":{str(int(k)):round(float(v),2) for k,v in vendor_one_trend.items()},"vendor_average_actual_lead_days":{k:round(float(v),2) for k,v in lead.items()},"highest_value_vendor_lead_days":round(float(lead.get("V0001",0)),2),"critical_stockout_sku_warehouse_rows":int(snapshot.RiskLevel.eq("Critical").sum()) if not snapshot.empty else 0,"negative_on_hand_sku_warehouse_rows":int(snapshot.AvailableQty.lt(0).sum()) if not snapshot.empty else 0,"dead_inventory_value":round(float((dead_stock.AvailableQty*dead_stock.UnitCost).sum()),2) if not dead_stock.empty else 0,"valuable_customers_inactive_over_60_days":int(len(at_risk)),"valuable_inactive_lifetime_revenue":round(float(at_risk.LifetimeRevenue.sum()),2),"snacks_discount_and_margin_by_year":{str(int(year)):{"discount_rate":round(float(row.Discount/(row.Revenue+row.Discount)),4),"gross_margin":round(float(row.GrossProfit/row.Revenue),4)} for year,row in snacks.iterrows() if row.Revenue>0},"health_2025_return_amount_rate":round(health_returns/health_sales,4) if health_sales else 0}
    dq_path=PROCESSED_DIR/"data_quality.csv"
    dq=pd.read_csv(dq_path) if dq_path.exists() else pd.DataFrame()
    dq_summary={"total_tests":int(len(dq)),"passed_tests":int(dq.Status.eq("PASS").sum()) if len(dq) else 0,"failed_tests":int(dq.Status.eq("FAIL").sum()) if len(dq) else 0,"failed_records":int(dq.FailedRecords.sum()) if len(dq) else 0,"quality_percent":round(float(dq.Status.eq("PASS").mean()*100),2) if len(dq) else None}
    rec_path=PROCESSED_DIR/"reconciliation.csv"
    reconciliation=pd.read_csv(rec_path).to_dict(orient="records") if rec_path.exists() else []
    if not snapshot.empty:
        snapshot["RiskRank"]=snapshot.RiskLevel.map({"Critical":1,"High Risk":2,"Watch":3,"Healthy":4,"Excess":5,"No Recent Sales":6})
        inv_top=snapshot.sort_values(["RiskRank","DaysOnHand"],na_position="first").head(500).drop(columns="RiskRank")
        safe_snapshot=inv_top.astype(object).where(pd.notna(inv_top),None)
    else: safe_snapshot=snapshot
    payload={
      "executive_kpis":{"revenue":float(monthly.Revenue.sum()),"gross_profit":float(monthly.GrossProfit.sum()),"gross_margin":float(monthly.GrossProfit.sum()/monthly.Revenue.sum()) if monthly.Revenue.sum() else 0,"units":int(monthly.Units.sum()),"orders":int(orders.SalesOrderID.nunique()),"customers":int(customers.CustomerID.nunique()),"inventory_value":float((snapshot.AvailableQty*snapshot.UnitCost).sum()) if not snapshot.empty else 0,"open_po_value":open_po_value},
      "sales_trend":monthly.to_dict(orient="records"),"sales_trend_by_region":region_trend.to_dict(orient="records"),"sales_by_category":category_summary.sort_values("Revenue",ascending=False).to_dict(orient="records"),"sales_by_region":region_summary.sort_values("Revenue",ascending=False).to_dict(orient="records"),"sales_by_rep":rep_summary.sort_values("Revenue",ascending=False).to_dict(orient="records"),"sales_by_channel":channel_summary.to_dict(orient="records"),"sales_detail":sales_product.nlargest(1500,"Revenue")[["InvoiceID","InvoiceDate","CustomerID","Region","SalesRepID","ProductID","SKU","ProductName","CategoryName","Channel","Quantity","Revenue","DiscountAmount","GrossProfit"]].to_dict(orient="records"),"customer_performance":customers.nlargest(500,"LifetimeRevenue").to_dict(orient="records"),"customer_segments":customer_segments.to_dict(orient="records"),"inventory_detail":safe_snapshot.to_dict(orient="records"),"vendor_performance":vendors.to_dict(orient="records"),"open_purchase_orders":open_po_detail.to_dict(orient="records"),"warehouse_performance":warehouse_summary.to_dict(orient="records"),"returns_by_reason":returns_by_reason.to_dict(orient="records"),"business_findings":findings,"data_quality":{"summary":dq_summary,"results":dq.to_dict(orient="records")},"reconciliation":reconciliation}
    WEB_DATA_DIR.mkdir(parents=True,exist_ok=True); write_json(payload,WEB_DATA_DIR/"dashboard.json")

if __name__=="__main__": export()
