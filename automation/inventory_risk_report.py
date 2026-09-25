"""Flag product/warehouse rows where yesterday demand consumes inventory quickly."""
from pathlib import Path
import pandas as pd
from utils.config import RAW_DIR, PROCESSED_DIR
from utils.helpers import write_csv

def run(source=RAW_DIR):
    tx=pd.read_csv(source/"InventoryTransaction.csv",parse_dates=["TransactionDate"])
    products=pd.read_csv(source/"Product.csv")
    if tx.empty: return pd.DataFrame()
    snapshot=tx.groupby(["ProductID","WarehouseID"],as_index=False).agg(AvailableInventory=("Quantity","sum"))
    as_of=tx.TransactionDate.max()
    yesterday=tx[tx.TransactionDate.eq(as_of-pd.Timedelta(days=1)) & tx.TransactionType.eq("Sales Shipment")].groupby(["ProductID","WarehouseID"]).Quantity.sum().abs()
    shipment=tx[(tx.TransactionType.eq("Sales Shipment"))&(tx.TransactionDate>as_of-pd.Timedelta(days=90))].copy()
    shipment["UnitsSold"]=shipment.Quantity.abs()
    trailing=shipment.groupby(["ProductID","WarehouseID"]).UnitsSold.sum().rename("Sales90Day")
    snapshot=snapshot.set_index(["ProductID","WarehouseID"])
    snapshot["YesterdayUnitsSold"]=yesterday.reindex(snapshot.index,fill_value=0)
    snapshot["Sales90Day"]=trailing.reindex(snapshot.index,fill_value=0)
    snapshot=snapshot.reset_index()
    detail=snapshot.merge(products[["ProductID","SKU","ProductName"]],on="ProductID",how="left")
    detail["DaysOnHand"]=detail.AvailableInventory.div(detail.Sales90Day/90).replace([float("inf"),-float("inf")],pd.NA)
    detail["PercentSold"]=detail.YesterdayUnitsSold.div(detail.AvailableInventory.where(detail.AvailableInventory.gt(0))).fillna(1)
    detail["RiskLevel"]=detail.DaysOnHand.map(lambda d:"No Recent Sales" if pd.isna(d) else "Critical" if d<7 else "High Risk" if d<14 else "Watch" if d<30 else "Healthy" if d<=90 else "Excess")
    po=pd.read_csv(source/"PurchaseOrderLine.csv").merge(pd.read_csv(source/"PurchaseOrderHeader.csv",parse_dates=["ExpectedDeliveryDate"])[["PONumber","WarehouseID","ExpectedDeliveryDate"]],on="PONumber")
    inbound=po[po.RemainingQuantity.gt(0)].groupby(["ProductID","WarehouseID"]).agg(InboundQuantity=("RemainingQuantity","sum"),ExpectedPODate=("ExpectedDeliveryDate","min"))
    detail=detail.merge(inbound,on=["ProductID","WarehouseID"],how="left").fillna({"InboundQuantity":0})
    cols=["SKU","ProductName","WarehouseID","YesterdayUnitsSold","AvailableInventory","PercentSold","DaysOnHand","InboundQuantity","ExpectedPODate","RiskLevel"]
    return detail.loc[(detail.PercentSold>.1)|(detail.RiskLevel.isin(["Critical","High Risk"])),cols]

if __name__=="__main__":
    result=run(); write_csv(result,PROCESSED_DIR/"inventory_risk_report.csv"); print(f"Flagged {len(result)} product/warehouse rows")
