# Metric contracts

| Metric | Definition | Scope / limitation |
|---|---|---|
| Revenue | SUM posted synthetic invoice-line Revenue | Excludes tax/freight; financial filters use invoice month and current customer region |
| Gross profit | SUM invoice-line GrossProfit | Generated revenue minus generated COGS; excludes rebates/overhead |
| Gross margin | GP / Revenue | Undefined at zero revenue; aggregate ratio, not average row margin |
| Orders | Distinct order headers by OrderDate | Bookings, including cancelled/open states; separate from invoices |
| Primary change badge | Selected period versus exact months one year earlier | Requires complete prior coverage; no ratio when prior denominator is zero |
| Margin movement | Current aggregate margin minus prior aggregate margin | Percentage points |
| Customers | Distinct customers with invoiced activity | Full-dataset snapshot; not filtered active-customer count |
| Net inventory | SUM signed ending quantity × current product cost | Includes negative positions; separate positive/negative values disclosed; not accounting valuation |
| Days on hand | max(ending quantity,0) / (90-day shipment units / 90) | Undefined at zero velocity; no-velocity stock classified separately |
| No-recent-movement stock | Positive quantity and no shipments in trailing 90 days | Investigation candidate, not necessarily obsolete or recoverable cash |
| Excess stock | Positive stock with >90 days coverage | Demonstration threshold, not an agreed corporate policy |
| Open PO value | RemainingQuantity × PO line UnitCost | All unreceived commitments; not all overdue |
| Overdue commitment | Open value where ExpectedDeliveryDate precedes business cutoff | Aging buckets: 0, 1–30, 31–90, 91+ days |
| On-time shipment rate | ActualShipDate <= RequestedShipDate among shipped orders | Not delivery OTIF; excludes unshipped orders |
| Vendor fill rate | Received / ordered quantity | Not on-time-in-full; receipts span periods |
| Inactive valuable customers | Lifetime revenue >= $25K and >60 days since last invoice | Lifetime revenue is not current revenue at risk; recent 90-day revenue is separately exported |
| Top-10 concentration | Top 10 customers' lifetime revenue / total | Full dataset; positive synthetic invoices |

Reconciliation uses exact totals: USD tolerance 0.01, units tolerance 0.000001. Currency formatting is never applied to units. SQLite REAL and pandas float calculations use explicit tolerance; production finance requires an approved decimal policy. Detail extracts disclose caps and do not necessarily sum to full-dataset KPI totals.
