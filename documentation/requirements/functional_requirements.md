# Functional Requirements

| ID | Requirement | Acceptance evidence |
|---|---|---|
| FR-01 | Generate linked fictional master and ERP transaction data for a three-year period | Generator emits CSVs with stable keys and reproducible seed |
| FR-02 | Distinguish order bookings from invoiced revenue | Sales order and invoice headers/lines remain separate |
| FR-03 | Build clean staging, date/customer/product/vendor/rep/warehouse dimensions, and sales/inventory/purchasing/returns facts | Executed SQLite DDL/load with enforced primary and foreign keys; T-SQL remains a separate design |
| FR-04 | Publish sales, customer, product, inventory, vendor, purchasing, warehouse, and executive marts | SQL monthly sales plus Python operational aggregates from validated staging |
| FR-05 | Detect duplicate, orphan, invalid, negative, and unreconciled data | Quality results include checked, failed, pass rate, status, run date |
| FR-06 | Reconcile raw, warehouse, and dashboard totals | Revenue, GP, units, inventory and PO value show variance |
| FR-07 | Export dashboard summaries and bounded details | Static JSON loads without a database or server |
| FR-08 | Provide overview, domain, trust, and project views, filtering, charts, searchable tables, responsive layout | Browser QA and screenshots |
| FR-09 | Produce three operational exception reports | Inventory risk, overdue POs, inactive valuable customers |

