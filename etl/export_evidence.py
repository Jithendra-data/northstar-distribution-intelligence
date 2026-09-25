"""Bounded investigation extracts and measured dataset coverage."""
import pandas as pd

def add_evidence(payload, stock, po, customers, sales, orders, receipts, source):
    f=payload['business_findings']
    positive=stock.AvailableQty.clip(lower=0)*stock.UnitCost
    negative=stock.AvailableQty.clip(upper=0)*stock.UnitCost
    f.update(positive_inventory_value=float(positive.sum()),negative_inventory_value=float(negative.sum()),
      excess_inventory_value=float(positive[pd.to_numeric(stock.DaysOnHand).fillna(0)>90].sum()),
      overdue_po_value=float(po.loc[(po.RemainingQuantity>0)&(po.DaysLate>0),'RemainingValue'].sum()))
    recent=sales[sales.InvoiceDate>sales.InvoiceDate.max()-pd.Timedelta(days=90)]
    inactive=customers[(customers.LifetimeRevenue>=25000)&(customers.DaysInactive>60)]
    f['inactive_recent_90d_revenue']=float(recent.loc[recent.CustomerID.isin(inactive.CustomerID),'Revenue'].sum())
    f['customer_top10_revenue_share']=float(customers.LifetimeRevenue.nlargest(10).sum()/customers.LifetimeRevenue.sum())
    shipped=orders.dropna(subset=['ActualShipDate']).copy()
    shipped['RequestedShipDate']=pd.to_datetime(shipped.RequestedShipDate)
    f['on_time_shipment_rate']=float((shipped.ActualShipDate<=shipped.RequestedShipDate).mean()) if len(shipped) else None
    f['po_aging']={label:float(po.loc[(po.RemainingQuantity>0)&(po.DaysLate.between(lo,hi)),'RemainingValue'].sum()) for label,lo,hi in [('Not late',0,0),('1-30 days',1,30),('31-90 days',31,90),('91+ days',91,99999)]}
    vy=receipts.assign(Year=receipts.CreatedDate.dt.year).groupby(['VendorID','Year']).ActualLeadDays.mean().unstack()
    if len(vy.columns)>1:
        changes=(vy.iloc[:,-1]-vy.iloc[:,0]).dropna()
        if not changes.empty:
            vendor=changes.idxmax()
            f['supplier_deterioration']={'VendorID':vendor,'ChangeDays':float(changes[vendor]),'FromYear':int(vy.columns[0]),'ToYear':int(vy.columns[-1]),'FromDays':float(vy.loc[vendor].iloc[0]),'ToDays':float(vy.loc[vendor].iloc[-1])}
    def records(frame): return frame.astype(object).where(frame.notna(),None).to_dict(orient='records')
    dead=stock[(stock.Sales90Day==0)&(stock.AvailableQty>0)].copy();dead['ExposureValue']=dead.AvailableQty*dead.UnitCost
    definitions={
      'inventory':(dead.sort_values('ExposureValue',ascending=False),['SKU','ProductName','WarehouseID','AvailableQty','ExposureValue'],'Positive stock with no shipments in trailing 90 days'),
      'customers':(inactive,['CustomerID','CustomerName','Region','LifetimeRevenue','DaysInactive'],'Lifetime revenue >= $25K and inactivity >60 days'),
      'purchasing':(po[(po.RemainingQuantity>0)&(po.DaysLate>0)].sort_values('RemainingValue',ascending=False),['PONumber','VendorID','VendorName','DaysLate','RemainingValue'],'Overdue unreceived PO lines, largest commitments first')}
    payload['investigations']={key:{'total':len(frame),'exported':min(500,len(frame)),'rule':rule,'rows':records(frame.head(500)[cols])} for key,(frame,cols,rule) in definitions.items()}
    specs=[('sales_by_category',len(payload['sales_by_category']),'All categories'),('customer_performance',len(customers),'Top 500 customers by lifetime revenue'),('inventory_detail',len(stock),'Top 500 positions by risk then days on hand'),('open_purchase_orders',int((po.RemainingQuantity>0).sum()),'First 500 open PO lines by expected date'),('vendor_performance',len(payload['vendor_performance']),'All vendors'),('warehouse_performance',len(payload['warehouse_performance']),'All warehouses'),('returns_by_reason',len(payload['returns_by_reason']),'All return reasons'),('sales_detail',len(sales),'Top 1,500 invoice lines by revenue')]
    payload['extract_coverage']={key:{'eligible':total,'exported':len(payload[key]),'selection':rule,'scope':'All dates and regions; search and download cover this extract only'} for key,total,rule in specs}
    payload['pipeline_metadata'].update(contract_version=2,data_through=str(orders.OrderDate.max().date()),valuation_policy='Signed ending quantity times current product unit cost. Negative positions included in net value and disclosed separately; not a financial inventory valuation.')
