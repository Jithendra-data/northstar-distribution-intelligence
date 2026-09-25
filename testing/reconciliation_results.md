# Reconciliation evidence

The current five results are published in web/data/dashboard.json and shown in Data Quality. Source totals read raw CSVs. Warehouse totals execute independent queries against loaded SQLite facts. Published totals come from the candidate dashboard contract. Units use a numeric format; monetary measures use USD. Both source-to-warehouse and source-to-published variances are displayed with explicit tolerances. Failed or missing comparisons block publication.
