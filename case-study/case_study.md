# NorthStar Distribution Intelligence Platform

## Executive summary
NorthStar is a fictional wholesale distributor. This portfolio project demonstrates the full path from ERP-style synthetic records to governed analytical models, operational exceptions, reconciliation, and an executive static web application.

## Business problem and requirements
Leadership needs a consistent view of invoiced growth and margin, customer retention, inventory exposure, supplier reliability, and fulfillment performance. Operational analysts need actionable exception lists. The solution preserves orders and invoices as separate business events and uses explicit fact grains and KPI definitions.

## Technical architecture and data sources
Deterministic Python-generated CSV data feeds raw, staging, SQL Server-compatible warehouse tables, marts, validation and reconciliation, then static JSON for a GitHub Pages dashboard. All entities and activity are synthetic.

## Database design and ETL
Dimensions: date, customer, product, vendor, sales rep, warehouse. Facts: invoice line, inventory movement, PO line, return line. FactSales is at invoice-line grain; see architecture documentation for all grains and relationships.

## KPI framework and analytics
The dashboard is designed to answer questions about revenue/margin, concentration and customer risk, stock coverage and dead stock, PO lateness and vendor costs, warehouse shipping delay, and returns. Scenario findings must be calculated from generated records and exported data.

## Calculated findings from the reproducible 2023–2025 run
The 75,000-order generated run produces $30.08M in invoiced revenue and $11.19M gross profit (37.2% gross margin). Revenue, gross profit, units, ending inventory value, and open PO value reconcile between the source-derived Python fact basis and dashboard export.

- Vendor V0001's actual receipt lead time rises from 10.9 days in 2023 to 16.4 in 2024 and 19.9 in 2025.
- Atlanta averages 4.68 order-to-ship days, compared with 1.80 in Denver.
- Inventory analysis surfaces 1,834 critical product/warehouse positions, including 1,948 with negative ending on-hand. Zero-velocity positive stock is valued at $3.70M.
- Twenty-one customers with at least $25K lifetime revenue are more than 60 days inactive; their calculated lifetime revenue is $2.35M.
- Snacks' discount rate rises from 6.1% in 2023 to 12.4% in 2025 while gross margin falls from 34.4% to 29.9%.
- Health returns reach 7.35% of 2025 category revenue by returned amount.
- The 20-test data quality run records one failed test: negative ending on-hand, with 1,948 affected product/warehouse positions. This is the intentionally injected stock availability scenario.

These figures are derived from generated CSVs by the export and validation scripts.

## Automation, quality and future roadmap
Three exception reports identify inventory risks, overdue purchasing commitments, and valuable inactive accounts. Quality checks and reconciliation expose source defects and measure parity across layers. Future extensions include incremental refresh, SQL Server load orchestration, forecast backtesting, and role-specific alert thresholds.
