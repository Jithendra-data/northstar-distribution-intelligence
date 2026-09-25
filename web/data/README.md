# Dashboard data exports

Run `python -m etl.export_dashboard_data` after generating source extracts. The command writes `dashboard.json` here. The static app reads this file using a relative fetch, so use a local static web server (for example, `python -m http.server 8000 --directory web`) instead of opening the HTML as `file://`.

