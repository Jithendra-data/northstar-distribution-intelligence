CREATE SCHEMA dw;
GO
CREATE TABLE dw.DimDate(DateKey int NOT NULL PRIMARY KEY, [Date] date NOT NULL UNIQUE, [Year] smallint NOT NULL, QuarterNumber tinyint NOT NULL, MonthNumber tinyint NOT NULL, MonthName varchar(12) NOT NULL, [Week] tinyint NOT NULL, [Day] tinyint NOT NULL, DayOfWeek tinyint NOT NULL, DayName varchar(12) NOT NULL, YearMonth char(7) NOT NULL, IsWeekend bit NOT NULL, FiscalYear smallint NOT NULL, FiscalQuarter tinyint NOT NULL);
CREATE TABLE dw.DimCustomer(CustomerKey int IDENTITY PRIMARY KEY, CustomerID varchar(8) NOT NULL UNIQUE, CustomerName varchar(160), CustomerGroup varchar(40), Region varchar(20), SalesRepID varchar(8), Status varchar(20));
CREATE TABLE dw.DimProduct(ProductKey int IDENTITY PRIMARY KEY, ProductID varchar(8) NOT NULL UNIQUE, SKU varchar(16), ProductName varchar(160), BrandID varchar(8), CategoryID varchar(8), CategoryName varchar(60), VendorID varchar(8), UnitCost decimal(12,2), StandardPrice decimal(12,2), DiscontinuedFlag bit);
CREATE TABLE dw.DimVendor(VendorKey int IDENTITY PRIMARY KEY, VendorID varchar(8) NOT NULL UNIQUE, VendorName varchar(160), State char(2), StandardLeadTimeDays smallint);
CREATE TABLE dw.DimSalesRep(SalesRepKey int IDENTITY PRIMARY KEY, SalesRepID varchar(8) NOT NULL UNIQUE, SalesRepName varchar(120), Region varchar(20), Territory varchar(40));
CREATE TABLE dw.DimWarehouse(WarehouseKey int IDENTITY PRIMARY KEY, WarehouseID char(3) NOT NULL UNIQUE, WarehouseName varchar(100), City varchar(60), State char(2));
GO

