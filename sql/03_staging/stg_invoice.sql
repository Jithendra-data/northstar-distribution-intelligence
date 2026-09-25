-- Type-safe posted invoice staging. Reject/orphan capture belongs in validation output.
CREATE SCHEMA stg;
GO
CREATE OR ALTER VIEW stg.InvoiceLine AS
SELECT LTRIM(RTRIM(i.InvoiceID)) AS InvoiceID, i.LineNumber, LTRIM(RTRIM(i.SalesOrderID)) AS SalesOrderID,
       LTRIM(RTRIM(i.ProductID)) AS ProductID, TRY_CONVERT(int,i.Quantity) AS Quantity,
       TRY_CONVERT(decimal(12,2),i.Revenue) AS Revenue, TRY_CONVERT(decimal(14,2),i.COGS) AS COGS,
       TRY_CONVERT(decimal(14,2),i.GrossProfit) AS GrossProfit, TRY_CONVERT(decimal(14,2),i.DiscountAmount) AS DiscountAmount
FROM raw.InvoiceLine i
WHERE NULLIF(LTRIM(RTRIM(i.InvoiceID)),'') IS NOT NULL;
GO

