# KPI Dictionary

| KPI | Definition and formula | Source / grain | Refresh | Limitations |
|---|---|---|---|---|
| Revenue | Net posted product revenue = SUM(InvoiceLine.Revenue) | Invoice line | Each export | Excludes tax and freight |
| Gross Profit | SUM(Revenue - COGS), stored as GrossProfit | Invoice line | Each export | Synthetic costs; no rebates/overhead |
| Gross Margin % | Gross Profit / Revenue | Aggregate of invoice lines | Each export | Null when revenue is zero |
| Orders | Distinct SalesOrderID by OrderDate | Order header | Each export | Bookings include cancelled/open states unless explicitly filtered |
| Average Order Value | Invoiced revenue / distinct invoiced orders | Invoice line/header | Each export | Not order booking value |
| Days on Hand | Available quantity / (90-day units / 90) | Product-warehouse snapshot | Each export | Uses trailing velocity; zero sales classified separately |
| Vendor Fill Rate | Received quantity / ordered quantity | PO line | Each export | Partial receipts may cross reporting periods |
| Order-to-Ship Days | ActualShipDate - OrderDate | Shipped order header | Each export | Atlanta queue is intentionally slower |
| Customer inactivity | As-of date - latest invoice date | Customer aggregate | Each export | Segment cutoffs are documented alongside query |

