-- Governed metric basis: net posted invoices only; order bookings live in the order mart.
SELECT SUM(Revenue) Revenue, SUM(GrossProfit) GrossProfit,
       SUM(GrossProfit)/NULLIF(SUM(Revenue),0) GrossMarginPct,
       SUM(Quantity) Units, COUNT(DISTINCT InvoiceID) Invoices
FROM dw.FactSales;
GO

