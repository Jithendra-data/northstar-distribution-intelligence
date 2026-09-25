CREATE SCHEMA mart;
GO
CREATE OR ALTER VIEW mart.SalesPerformance AS
SELECT d.YearMonth, c.Region, p.CategoryName, SUM(f.Revenue) Revenue, SUM(f.GrossProfit) GrossProfit,
       SUM(f.Quantity) Units, COUNT(DISTINCT f.InvoiceID) Invoices,
       CAST(SUM(f.GrossProfit)/NULLIF(SUM(f.Revenue),0) AS decimal(9,4)) GrossMarginPct
FROM dw.FactSales f JOIN dw.DimDate d ON d.DateKey=f.DateKey
JOIN dw.DimCustomer c ON c.CustomerKey=f.CustomerKey JOIN dw.DimProduct p ON p.ProductKey=f.ProductKey
GROUP BY d.YearMonth,c.Region,p.CategoryName;
GO

