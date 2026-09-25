-- Raw landing tables intentionally retain source columns and permit source defects.
CREATE SCHEMA raw;
GO
CREATE TABLE raw.InvoiceHeader (InvoiceID varchar(12), SalesOrderID varchar(12), CustomerID varchar(8), InvoiceDate date, InvoiceStatus varchar(20));
CREATE TABLE raw.InvoiceLine (InvoiceID varchar(12), LineNumber int, SalesOrderID varchar(12), ProductID varchar(8), Quantity int, UnitPrice decimal(12,2), DiscountAmount decimal(14,2), Revenue decimal(14,2), UnitCost decimal(12,2), COGS decimal(14,2), GrossProfit decimal(14,2));
CREATE TABLE raw.SalesOrderHeader (SalesOrderID varchar(12), CustomerID varchar(8), SalesRepID varchar(8), WarehouseID char(3), OrderDate date, RequestedShipDate date, ActualShipDate date, OrderStatus varchar(20), Channel varchar(30), CustomerPO varchar(24), OrderCreatedTimestamp datetime2);
CREATE TABLE raw.SalesOrderLine (SalesOrderID varchar(12), LineNumber int, ProductID varchar(8), Quantity int, UnitPrice decimal(12,2), DiscountPercent decimal(7,4), DiscountAmount decimal(14,2), LineRevenue decimal(14,2), UnitCost decimal(12,2), LineCOGS decimal(14,2), GrossProfit decimal(14,2));
CREATE TABLE raw.PurchaseOrderHeader (PONumber varchar(12), VendorID varchar(8), WarehouseID char(3), CreatedDate date, ExpectedDeliveryDate date, POStatus varchar(24), CreatedBy varchar(80));
CREATE TABLE raw.PurchaseOrderLine (PONumber varchar(12), LineNumber int, ProductID varchar(8), OrderedQuantity int, ReceivedQuantity int, RemainingQuantity int, UnitCost decimal(12,2), LineAmount decimal(14,2));
CREATE TABLE raw.InventoryTransaction (InventoryTransactionID varchar(16), ProductID varchar(8), WarehouseID char(3), TransactionDate date, TransactionType varchar(24), Quantity decimal(14,2), ReferenceNumber varchar(20), UnitCost decimal(12,2));
GO

