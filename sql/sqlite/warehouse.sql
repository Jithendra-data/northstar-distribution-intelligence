-- Executed reference warehouse. SQLite natural keys; T-SQL remains a separate design.
PRAGMA foreign_keys = ON;
CREATE TABLE DimDate(DateKey TEXT PRIMARY KEY, YearMonth TEXT NOT NULL);
CREATE TABLE DimCustomer(CustomerID TEXT PRIMARY KEY, CustomerName TEXT, Region TEXT);
CREATE TABLE DimProduct(ProductID TEXT PRIMARY KEY, ProductName TEXT, CategoryName TEXT, UnitCost REAL NOT NULL);
CREATE TABLE DimWarehouse(WarehouseID TEXT PRIMARY KEY, WarehouseName TEXT);
CREATE TABLE DimVendor(VendorID TEXT PRIMARY KEY, VendorName TEXT);
CREATE TABLE DimSalesRep(SalesRepID TEXT PRIMARY KEY, SalesRepName TEXT);
CREATE TABLE FactSales(InvoiceID TEXT, LineNumber INTEGER, DateKey TEXT NOT NULL REFERENCES DimDate,
 CustomerID TEXT NOT NULL REFERENCES DimCustomer, ProductID TEXT NOT NULL REFERENCES DimProduct,
 WarehouseID TEXT NOT NULL REFERENCES DimWarehouse, SalesRepID TEXT NOT NULL REFERENCES DimSalesRep,
 Quantity REAL NOT NULL, Revenue REAL NOT NULL, GrossProfit REAL NOT NULL,
 PRIMARY KEY(InvoiceID,LineNumber));
CREATE TABLE FactInventory(InventoryTransactionID TEXT PRIMARY KEY, ProductID TEXT NOT NULL REFERENCES DimProduct,
 WarehouseID TEXT NOT NULL REFERENCES DimWarehouse, DateKey TEXT NOT NULL REFERENCES DimDate, Quantity REAL NOT NULL);
CREATE TABLE FactPurchasing(PONumber TEXT, LineNumber INTEGER, ProductID TEXT NOT NULL REFERENCES DimProduct,
 VendorID TEXT NOT NULL REFERENCES DimVendor, WarehouseID TEXT NOT NULL REFERENCES DimWarehouse,
 DateKey TEXT NOT NULL REFERENCES DimDate, RemainingQuantity REAL NOT NULL, UnitCost REAL NOT NULL,
 PRIMARY KEY(PONumber,LineNumber));
CREATE TABLE FactReturns(ReturnID TEXT PRIMARY KEY, CustomerID TEXT NOT NULL REFERENCES DimCustomer,
 ProductID TEXT NOT NULL REFERENCES DimProduct, DateKey TEXT NOT NULL REFERENCES DimDate,
 ReturnQuantity REAL NOT NULL, ReturnAmount REAL NOT NULL);
CREATE INDEX ix_sales_date_customer ON FactSales(DateKey,CustomerID);
CREATE INDEX ix_inventory_product_warehouse ON FactInventory(ProductID,WarehouseID);
CREATE VIEW MonthlySales AS SELECT d.YearMonth, SUM(f.Revenue) Revenue, SUM(f.GrossProfit) GrossProfit,
 SUM(f.Quantity) Units, COUNT(DISTINCT f.InvoiceID) Invoices FROM FactSales f
 JOIN DimDate d ON d.DateKey=f.DateKey GROUP BY d.YearMonth;
