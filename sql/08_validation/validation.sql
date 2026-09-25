-- Example source checks; all are expected to return zero exception rows on clean domains.
SELECT InvoiceID, COUNT(*) DuplicateCount FROM raw.InvoiceHeader GROUP BY InvoiceID HAVING COUNT(*)>1;
SELECT l.InvoiceID,l.LineNumber FROM raw.InvoiceLine l LEFT JOIN raw.InvoiceHeader h ON h.InvoiceID=l.InvoiceID WHERE h.InvoiceID IS NULL;
SELECT * FROM raw.SalesOrderLine WHERE Quantity<0;
SELECT * FROM raw.PurchaseOrderLine WHERE ReceivedQuantity>OrderedQuantity;
GO

