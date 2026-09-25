# NorthStar Distribution Intelligence Platform

[![Live Dashboard](https://img.shields.io/badge/Live-Dashboard-168575?style=for-the-badge)](https://jithendra-data.github.io/northstar-distribution-intelligence/)
[![Refresh Workflow](https://img.shields.io/badge/GitHub_Actions-Refresh_Pipeline-2f6fed?style=for-the-badge)](https://github.com/Jithendra-data/northstar-distribution-intelligence/actions/workflows/refresh-data.yml)
[![GitHub Pages](https://img.shields.io/badge/Hosted_on-GitHub_Pages-222?style=for-the-badge)](https://jithendra-data.github.io/northstar-distribution-intelligence/)

An end-to-end synthetic ERP analytics portfolio project for a fictional wholesale distributor. It demonstrates Python data generation, SQL Server-compatible modeling, analytics engineering, quality controls, reconciliation, operational reports, and a static executive dashboard.

> **Portfolio Project — All data shown in this application is synthetically generated and does not represent any real company, customer, vendor, or transaction.**

## 30-second project summary

NorthStar turns fictional ERP-style distribution records into a public executive analytics experience. The project generates linked orders, invoices, purchasing, inventory, customer, product, vendor, and return records; models them into SQL-friendly facts, dimensions, and marts; runs quality and reconciliation controls; exports dashboard-ready JSON; and publishes a hosted GitHub Pages dashboard.

## Project highlights

- Automated synthetic ERP refresh through GitHub Actions with traceable scenario seed and timestamp.
- Star schema design with invoice, inventory, purchasing, and returns fact grains.
- Quality and reconciliation controls that expose duplicate, orphan, date, relationship, and inventory exceptions.
- Hosted dashboard with executive KPIs, date/region filters, charts, paged tables, search, and CSV exports.
- Public documentation covering requirements, architecture, KPI definitions, data dictionary, operations, and case study.

## Live project

- **Dashboard:** https://jithendra-data.github.io/northstar-distribution-intelligence/
- **Refresh workflow:** https://github.com/Jithendra-data/northstar-distribution-intelligence/actions/workflows/refresh-data.yml
- **Case study:** [case-study/case_study.md](case-study/case_study.md)
- **Architecture guide:** [documentation/architecture/architecture.md](documentation/architecture/architecture.md)
- **Pipeline operations:** [documentation/operations/pipeline_operations.md](documentation/operations/pipeline_operations.md)

## Current published scenario

Latest dashboard export currently published in this repository:

| Metric | Value |
|---|---:|
| Scenario seed | `36084094524` |
| Invoiced revenue | `$27.97M` |
| Gross profit | `$10.35M` |
| Gross margin | `37.0%` |
| Sales orders | `75,000` |
| Customers with invoiced activity | `4,982` |
| Inventory value | `$6.62M` |
| Open PO value | `$4.19M` |
| Quality controls reviewed | `20` |
| Inventory positions flagged for review | `1,959` |

## Business questions answered

- Where are revenue and gross margin improving or slipping?
- Which products, regions, and customers drive commercial performance?
- Which inventory positions create stockout or working capital risk?
- Which vendors and warehouses affect service reliability?
- Which customer segments show inactivity or retention risk?

## Architecture

```text
Synthetic ERP → Raw CSV → Staging SQL → Star schema → Analytics marts
                                                   ├─ Quality/reconciliation
                                                   ├─ Python exception reports
                                                   └─ JSON → HTML/CSS/JS dashboard → GitHub Pages
```

## Technology

Python, pandas, NumPy, Faker, SQL Server-compatible T-SQL, analytics marts, data quality checks, GitHub Actions, GitHub Pages, HTML5, CSS3, JavaScript, Apache ECharts.

## Generate data locally

```bash
python -m pip install -r requirements.txt
python -m etl.run_pipeline
```

The default configuration generates 5,000 customers, 2,000 products, 150 vendors, 25 reps, 75,000 orders and 10,000 purchase orders over 2023–2025 with a fixed local seed, then cleans, summarizes, validates, reconciles, and exports. Use `--orders 1000 --purchase-orders 250` for a smaller generated run or `--skip-generation` to reuse existing raw extracts. Raw CSVs are written under `data/raw/` and are excluded from Git by default.

## Project layout

`python/` generators and ETL; `sql/` database layers and marts; `validation/` quality and reconciliation; `automation/` exception reports; `web/` static application and JSON; `documentation/` requirements, architecture, dictionaries and strategy; `case-study/` narrative.

## Dashboard and publishing

Run `python -m etl.run_pipeline`, then serve locally with `python -m http.server 8000 --directory web` and open `http://localhost:8000`. The dashboard has executive filters, calculated scenario findings, searchable/sortable paged detail tables, CSV downloads, architecture, documentation, data quality, and reconciliation views. The included Pages workflow deploys the `web/` directory on pushes to `main`; enable GitHub Pages with **GitHub Actions** as the build source. The dashboard requires no database server.

## Automated refresh and pipeline visibility

`Refresh synthetic analytics data` runs every Monday and can also be started from the repository's **Actions** tab. Each run assigns a new seed or uses the seed supplied on a manual run, generates a complete fictional ERP scenario, cleans and models it, runs quality and reconciliation checks, publishes a new `web/data/dashboard.json`, and commits the refreshed dashboard data to `main`. That commit triggers the Pages deployment workflow.

Every refresh run retains a 14-day `northstar-pipeline-evidence` artifact with the generated dashboard contract, data-quality output, and reconciliation output. Use the Actions logs and [pipeline operations guide](documentation/operations/pipeline_operations.md) to inspect each step, input seed, control result, and deployment.

## Analytics and controls

Order bookings and posted invoice revenue are separate. Inventory is derived from movements. KPI definitions live in `documentation/kpi_dictionary/`; reconciliation and quality results are generated by the pipeline. See the architecture and case study for business questions, data grains and scenario design.

## License

This project is released under the MIT License. See [LICENSE](LICENSE).
