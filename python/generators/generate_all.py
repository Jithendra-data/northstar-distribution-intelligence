"""Generate a deterministic ERP-style dataset. Orders, invoices and inventory are distinct."""
from __future__ import annotations

import argparse
import numpy as np
import pandas as pd

from python.generators.generate_master_data import create_master_data
from utils.config import END_DATE, NUM_PURCHASE_ORDERS, NUM_SALES_ORDERS, RAW_DIR, RANDOM_SEED, START_DATE
from utils.helpers import write_csv

def build_transactions(m: dict[str, pd.DataFrame], orders_n: int, pos_n: int) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(RANDOM_SEED)
    start, end = pd.Timestamp(START_DATE), pd.Timestamp(END_DATE)
    days = pd.date_range(start, end, freq="D")
    # Weekdays, monthly seasonality, gradual growth and a growing household-products family.
    month_lift = np.array([1,1,1.05,1.1,1.15,1.2,1.25,1.15,1.1,1.15,1.35,1.45])
    weights = np.array([0.27 if d.dayofweek < 5 else 0.05 for d in days]) * month_lift[days.month - 1] * np.linspace(.82, 1.18, len(days))
    order_days = rng.choice(days.to_numpy(), size=orders_n, p=weights / weights.sum())
    customers, products, reps, whs, vendors = (m[k] for k in ["Customer", "Product", "SalesRep", "Warehouse", "Vendor"])
    cust_prob = np.arange(1, len(customers)+1, dtype=float) ** -0.72; cust_prob /= cust_prob.sum()
    prod_prob = np.arange(1, len(products)+1, dtype=float) ** -0.62; prod_prob /= prod_prob.sum()
    headers, lines, invoice_headers, invoice_lines, returns, invtx = [], [], [], [], [], []
    # Starting balances are explicit ledger events, so the ending snapshot can be derived.
    for p in products.itertuples(index=False):
        for wh in whs.itertuples(index=False):
            # Long-tail SKUs intentionally start with stock that can become dead inventory.
            opening = int(rng.integers(120, 300) if p.ProductID[-2:] in {"03", "17", "41"} else rng.integers(2, 10) if p.CategoryName=="Cleaning" else rng.integers(5, 30))
            invtx.append({"InventoryTransactionID":f"IT{len(invtx)+1:08}","ProductID":p.ProductID,"WarehouseID":wh.WarehouseID,"TransactionDate":start,"TransactionType":"Opening Balance","Quantity":opening,"ReferenceNumber":"OPENING-2023","UnitCost":p.UnitCost})
    family_ids = set(products.loc[products.CategoryName.eq("Cleaning"), "ProductID"])
    # Twenty historically high-value accounts progressively leave the portfolio.
    churn_ids = set(customers.iloc[:20].CustomerID)
    churn_indices = np.flatnonzero(customers.CustomerID.isin(churn_ids).to_numpy())
    for n, raw_day in enumerate(order_days, 1):
        day = pd.Timestamp(raw_day)
        churn_cutoff = 0.0 if day < pd.Timestamp("2024-01-01") else min(1.0, (day-pd.Timestamp("2024-01-01")).days/500)
        customer_probs = cust_prob.copy()
        customer_probs[churn_indices] *= max(0.0, 1-churn_cutoff)
        customer_probs /= customer_probs.sum()
        ci = int(rng.choice(len(customers), p=customer_probs)); customer = customers.iloc[ci]
        wh = whs.iloc[int(rng.choice(4, p=[.27,.28,.25,.20]))]
        rep = customer.SalesRepID
        channel = rng.choice(["Direct Sales","Online","Key Accounts","Marketplace","Inside Sales"], p=[.28,.2,.14,.13,.25])
        # Atlanta intentionally has a longer queue; cancellations/backorders remain explicit.
        base = {"DEN":1.8,"DAL":2.1,"CHI":2.4,"ATL":4.7}[wh.WarehouseID]
        ship_days = max(0, int(round(rng.normal(base, .8))))
        status = rng.choice(["Invoiced","Shipped","Backordered","Cancelled","Open"], p=[.79,.08,.07,.03,.03])
        order_id = f"SO{n:07}"
        headers.append({"SalesOrderID":order_id,"CustomerID":customer.CustomerID,"SalesRepID":rep,"WarehouseID":wh.WarehouseID,"OrderDate":day,"RequestedShipDate":day+pd.Timedelta(days=2),"ActualShipDate":min(end,day+pd.Timedelta(days=ship_days)) if status in ["Invoiced","Shipped"] else pd.NaT,"OrderStatus":status,"Channel":channel,"CustomerPO":f"PO-{n:07}","OrderCreatedTimestamp":day+pd.Timedelta(hours=int(rng.integers(7,18)))})
        li_count = int(rng.choice([1,2,3,4,5,6], p=[.18,.26,.25,.17,.09,.05])); order_rows=[]
        for ln in range(1, li_count+1):
            pi = int(rng.choice(len(products), p=prod_prob)); p = products.iloc[pi]
            # Product family demand accelerates in the final 18 months.
            qty = int(max(1, rng.negative_binomial(2, .42)+1))
            if p.ProductID in family_ids and day >= pd.Timestamp("2024-07-01"): qty = int(np.ceil(qty * 1.6))
            discount = float(rng.uniform(.03,.22) if p.CategoryName == "Snacks" and day.year == 2025 else rng.uniform(0,.12))
            price = float(p.StandardPrice); discount_amount = round(price * qty * discount, 2); revenue = round(price*qty-discount_amount, 2)
            cost = float(p.UnitCost) * (1.12 if p.VendorID == "V0001" and day >= pd.Timestamp("2024-10-01") else 1)
            gp = round(revenue - cost*qty, 2)
            row={"SalesOrderID":order_id,"LineNumber":ln,"ProductID":p.ProductID,"Quantity":qty,"UnitPrice":price,"DiscountPercent":round(discount,4),"DiscountAmount":discount_amount,"LineRevenue":revenue,"UnitCost":round(cost,2),"LineCOGS":round(cost*qty,2),"GrossProfit":gp}
            lines.append(row); order_rows.append((row,p))
        if status == "Invoiced":
            invoice_id=f"INV{n:07}"; invoice_date=min(end,day+pd.Timedelta(days=ship_days)); invoice_headers.append({"InvoiceID":invoice_id,"SalesOrderID":order_id,"CustomerID":customer.CustomerID,"InvoiceDate":invoice_date,"InvoiceStatus":"Posted"})
            for row,p in order_rows:
                invoice_lines.append({"InvoiceID":invoice_id,"LineNumber":row["LineNumber"],"SalesOrderID":order_id,"ProductID":row["ProductID"],"Quantity":row["Quantity"],"UnitPrice":row["UnitPrice"],"DiscountAmount":row["DiscountAmount"],"Revenue":row["LineRevenue"],"UnitCost":row["UnitCost"],"COGS":row["LineCOGS"],"GrossProfit":row["GrossProfit"]})
                invtx.append({"InventoryTransactionID":f"IT{len(invtx)+1:08}","ProductID":p.ProductID,"WarehouseID":wh.WarehouseID,"TransactionDate":invoice_date,"TransactionType":"Sales Shipment","Quantity":-row["Quantity"],"ReferenceNumber":order_id,"UnitCost":row["UnitCost"]})
                return_prob=.18 if p.CategoryName=="Health" and day>=pd.Timestamp("2025-01-01") else .025
                if rng.random()<return_prob:
                    return_id=f"RT{len(returns)+1:07}"; returned=max(1,int(row["Quantity"]*rng.uniform(.2,.7)))
                    amount=round(row["UnitPrice"]*returned*(1-row["DiscountPercent"]),2)
                    reason=rng.choice(["Quality Issue","Damaged","Shipping Damage","Wrong Product","Customer Changed Mind","Short Dated","Other"])
                    return_date=min(end,day+pd.Timedelta(days=int(rng.integers(4,35))))
                    returns.append({"ReturnID":return_id,"SalesOrderID":order_id,"InvoiceID":invoice_id,"CustomerID":customer.CustomerID,"ProductID":p.ProductID,"ReturnDate":return_date,"ReturnQuantity":returned,"ReturnReason":reason,"ReturnAmount":amount})
                    invtx.append({"InventoryTransactionID":f"IT{len(invtx)+1:08}","ProductID":p.ProductID,"WarehouseID":wh.WarehouseID,"TransactionDate":return_date,"TransactionType":"Customer Return","Quantity":returned,"ReferenceNumber":return_id,"UnitCost":row["UnitCost"]})
    po_headers=[]; po_lines=[]; receipts=[]
    for n in range(1,pos_n+1):
        created=pd.Timestamp(rng.choice(days.to_numpy())); vi=int(rng.integers(0,len(vendors))); vendor=vendors.iloc[vi]; wh=whs.iloc[int(rng.integers(0,4))]
        deterioration=min(1.0,max(0.0,(created-pd.Timestamp("2023-01-01")).days/900))
        lead=int(rng.integers(8,11) if vendor.VendorID=="V0001" and created < pd.Timestamp("2023-10-01") else rng.integers(18,21) if vendor.VendorID=="V0001" and created >= pd.Timestamp("2025-06-01") else round(8+11*deterioration) if vendor.VendorID=="V0001" else vendor.StandardLeadTimeDays)
        expected=created+pd.Timedelta(days=lead); po=f"PO{n:06}"; line_count=int(rng.choice([2,3,4,5,6],p=[.12,.24,.32,.22,.10]))
        po_headers.append({"PONumber":po,"VendorID":vendor.VendorID,"WarehouseID":wh.WarehouseID,"CreatedDate":created,"ExpectedDeliveryDate":expected,"POStatus":"Open","CreatedBy":"Synthetic Procurement"})
        line_receipts=[]
        for line_no in range(1,line_count+1):
            # Replenishment does not catch up once elevated family demand emerges.
            eligible=products if created < pd.Timestamp("2024-07-01") else products.loc[~products.ProductID.isin(family_ids)]
            p=eligible.iloc[int(rng.integers(0,len(eligible)))]; ordered=int(rng.integers(8,36)); is_closed=expected<=end and rng.random()<.77
            received=ordered if is_closed else int(ordered*rng.uniform(.25,.8)) if expected<=end and rng.random()<.5 else 0
            line_receipts.append((ordered,received))
            po_lines.append({"PONumber":po,"LineNumber":line_no,"ProductID":p.ProductID,"OrderedQuantity":ordered,"ReceivedQuantity":received,"RemainingQuantity":ordered-received,"UnitCost":p.UnitCost,"LineAmount":ordered*p.UnitCost})
            if received:
                receipt_date=min(end,expected+pd.Timedelta(days=int(rng.integers(-2,6)))); receipts.append({"ReceiptID":f"RC{len(receipts)+1:07}","PONumber":po,"ProductID":p.ProductID,"ReceiptDate":receipt_date,"QuantityReceived":received,"WarehouseID":wh.WarehouseID})
                invtx.append({"InventoryTransactionID":f"IT{len(invtx)+1:08}","ProductID":p.ProductID,"WarehouseID":wh.WarehouseID,"TransactionDate":receipt_date,"TransactionType":"Purchase Receipt","Quantity":received,"ReferenceNumber":po,"UnitCost":p.UnitCost})
        ordered_total=sum(x[0] for x in line_receipts); received_total=sum(x[1] for x in line_receipts)
        po_headers[-1]["POStatus"]="Fully Received" if received_total==ordered_total else "Partially Received" if received_total else "Open"
    # Intentional but documented dirty records for the quality demonstration.
    return {"SalesOrderHeader":pd.DataFrame(headers),"SalesOrderLine":pd.DataFrame(lines),"InvoiceHeader":pd.DataFrame(invoice_headers),"InvoiceLine":pd.DataFrame(invoice_lines),"PurchaseOrderHeader":pd.DataFrame(po_headers),"PurchaseOrderLine":pd.DataFrame(po_lines),"PurchaseReceipt":pd.DataFrame(receipts),"InventoryTransaction":pd.DataFrame(invtx),"CustomerReturn":pd.DataFrame(returns)}

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orders",type=int,default=NUM_SALES_ORDERS)
    parser.add_argument("--purchase-orders",type=int,default=NUM_PURCHASE_ORDERS)
    parser.add_argument("--output",default=str(RAW_DIR))
    args=parser.parse_args()
    out=__import__("pathlib").Path(args.output); out.mkdir(parents=True,exist_ok=True)
    master=create_master_data()
    for name,frame in {**master,**build_transactions(master,args.orders,args.purchase_orders)}.items(): write_csv(frame,out/f"{name}.csv")
    print(f"Wrote synthetic ERP CSVs to {out}")

if __name__ == "__main__": main()
