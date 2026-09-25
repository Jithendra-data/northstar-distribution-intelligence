# Business Requirements

## Company and purpose
NorthStar Distribution is a fictional US wholesale distributor serving roughly 5,000 trade customers from Denver, Dallas, Chicago, and Atlanta. This portfolio system demonstrates how synthetic ERP transactions can become trusted operational and executive insight. No real employer, customer, vendor, or transaction data is used.

## Stakeholders and decisions
| Stakeholder | Decisions supported |
|---|---|
| Executive leadership | Growth, gross profit, concentration, working capital |
| Sales leadership | Territory performance, retention, discount discipline |
| Inventory planning | Replenishment, stockout exposure, excess and dead stock |
| Procurement | Supplier reliability, open commitments, cost movement |
| Warehouse operations | Fulfillment speed, backlog, returns |
| Data/BI team | Reconciliation, lineage, quality exceptions, refresh |

## Business problems
The synthetic scenario includes vendor lead-time deterioration and cost increases, demand growth without matching supply, high-value customer inactivity, excess inventory, discount-led margin loss, a product return spike, and Atlanta fulfillment delays. Reports must calculate evidence from generated records rather than use fixed findings.

## Reporting requirements
Provide invoiced revenue separately from booked orders; gross profit and margin; customer recency and concentration; inventory coverage and inbound supply; PO lateness and supplier fill; warehouse ship time; return rates; and source-to-dashboard reconciliation. Users need date and relevant business-dimension filters, searchable detail, and CSV export where practical.

## Functional requirements
- Reproducibly generate linked synthetic master and transactional entities.
- Preserve raw values, clean into staging, and publish a documented star schema and analytics marts.
- Calculate operational KPIs and data quality checks from those entities.
- Export compact static JSON for a serverless HTML dashboard.
- Produce inventory risk, overdue PO, and inactive customer reports.

## Non-functional requirements
Portable relative paths; seed and input hashes; executed SQLite reference plus SQL Server design; GitHub Pages compatible dashboard; responsive desktop-first design; traceable KPI definitions; explicit synthetic-data notice; no secrets; manageable browser payloads.

