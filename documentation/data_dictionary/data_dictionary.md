# Data Dictionary (initial core entities)

| Table | Column | Type | Description | Business meaning |
|---|---|---|---|---|
| Customer | CustomerID | varchar(8) | Synthetic stable identifier | Customer natural key |
| Customer | CustomerGroup | varchar(40) | Commercial segment | Supports cohort and mix analysis |
| Product | ProductID | varchar(8) | Synthetic stable identifier | Product natural key |
| Product | UnitCost | decimal(12,2) | Current synthetic standard cost | Cost basis for gross profit |
| SalesOrderHeader | SalesOrderID | varchar(12) | Booking identifier | Order lifecycle, not revenue |
| SalesOrderLine | LineRevenue | decimal(14,2) | Net booked line amount | Order booking value |
| InvoiceHeader | InvoiceID | varchar(12) | Posted invoice identifier | Revenue recognition event |
| InvoiceLine | Revenue | decimal(14,2) | Net invoiced amount | Revenue fact source |
| PurchaseOrderLine | RemainingQuantity | int | Ordered less received | Outstanding commitment |
| InventoryTransaction | Quantity | decimal(14,2) | Signed inventory movement | Source for on-hand calculation |
| CustomerReturn | ReturnAmount | decimal(14,2) | Value of returned goods | Return exposure |

All names, addresses, transactions and identifiers are generated. Full warehouse key/type details are maintained in the SQL DDL and extended as entities are implemented.

