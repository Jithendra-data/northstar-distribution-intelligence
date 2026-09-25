# Pipeline Operations Guide

## What starts a refresh

The `Refresh synthetic analytics data` workflow runs every Monday at 10:00 UTC. From the repository's **Actions** tab, choose the workflow and select **Run workflow** for an on-demand refresh. You can provide a seed to reproduce a scenario or leave it blank to use the GitHub workflow run ID as a new seed.

## What happens in a run

1. GitHub checks out the `main` branch and installs the pinned Python dependencies.
2. The generator writes fictional ERP extracts for master data, orders, invoices, purchase orders, receipts, inventory movements, and returns.
3. The ETL pipeline cleans the extracts and calculates sales, margin, customer, inventory, vendor, warehouse, and returns analytics.
4. Quality checks test uniqueness, relationships, dates, quantities, product costs, and ending inventory balances.
5. Reconciliation compares source calculations, analytic outputs, and the dashboard contract for revenue, gross profit, units, inventory value, and open PO value.
6. The exporter writes `web/data/dashboard.json`, including the scenario seed and refresh timestamp.
7. GitHub Actions saves the dashboard contract and control results as a 14-day artifact, then commits the refreshed dashboard JSON to `main`.
8. The Pages deployment workflow publishes the new dashboard version.

## How to inspect a run

Open the repository's **Actions** tab and select a refresh run. The logs show each stage and print the quality and reconciliation tables. The `northstar-pipeline-evidence` artifact contains the exact dashboard JSON, quality results, and reconciliation results produced by that run. The dashboard notice displays the seed and UTC refresh timestamp of its current scenario.

## Important operating notes

The project intentionally generates fictional data. A non-passing negative ending-inventory test is a designed scenario signal, surfaced in the dashboard as inventory risk; other quality and reconciliation controls should pass. Scheduled GitHub workflows are best effort and can be delayed by GitHub's scheduler. Manual runs provide an immediate refresh path.
