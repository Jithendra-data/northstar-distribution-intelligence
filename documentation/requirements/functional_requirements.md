# Functional Requirements

| ID | Requirement | Acceptance evidence |
|---|---|---|
| FR-01 | Generate linked fictional master and ERP transaction data for a three-year period | Generator emits CSVs with stable keys and reproducible seed |
| FR-02 | Distinguish order bookings from invoiced revenue | Sales order and invoice headers/lines remain separate |
| FR-03 | Build clean staging, date/customer/product/vendor/rep/warehouse dimensions, and sales/inventory/purchasing/returns facts | SQL DDL and transformations document grain and key constraints |
| FR-04 | Publish sales, customer, product, inventory, vendor, purchasing, warehouse, and executive marts | SQL queries define measures from source facts |
| FR-05 | Detect duplicate, orphan, invalid, negative, and unreconciled data | Quality results include checked, failed, pass rate, status, run date |
| FR-06 | Reconcile raw, warehouse, and dashboard totals | Revenue, GP, units, inventory and PO value show variance |
| FR-07 | Export dashboard summaries and bounded details | Static JSON loads without a database or server |
| FR-08 | Provide nine business-facing pages, filtering, charts, searchable tables, responsive layout | Browser QA and screenshots |
| FR-09 | Produce three operational exception reports | Inventory risk, overdue POs, inactive valuable customers |

