# Technical decisions and operational evidence

## ADR 1 — Static public delivery

Decision: keep GitHub Pages with bounded JSON extracts. Reason: reproducible public review without credentials or service cost. Trade-off: no private data, unrestricted queries, or server-side authorization. Rejected for this demonstration: a permanently running API with no demonstrated need. Migration trigger: confidential data or drill-through that cannot fit a bounded extract.

## ADR 2 — Executed SQLite reference warehouse

Decision: use Python's SQLite runtime for a tested dimensional load and independent SQL reconciliation. T-SQL remains a distinct design. Benefits: portable CI and enforced keys. Limits: single-build usage, natural keys, Type 1 current master attributes, binary floating-point aggregates with explicit tolerance. A finance production deployment would use audited decimal/integer-money policies and approved cost accounting.

## ADR 3 — Full rebuild and publication gate

Decision: full rebuilds at current synthetic scale. The integration test reruns identical source files and checks equal KPIs. A candidate passes blocking source controls, FK/PK loading, contract checks, and five reconciliations before replacing the public contract. The one allowed exception is negative ending inventory in the synthetic scenario. The exception does not authorize unexpected duplicate, orphan, or reconciliation failures.

The SQLite file is built under a candidate name; a failed build leaves the prior database intact. The last public JSON is not touched on candidate failure. Processed CSV diagnostics are not themselves an atomic published dataset. The Actions artifact captures the successful run's database and manifests.

## ADR 4 — Comparison semantics

The primary number and movement badge refer to the same selected period. Each selected month maps to the same month one year earlier. Partial history, no matching observations, and zero denominators are not reported as zero growth. Reversed dates leave the last valid results visible with an input error. Monthly sparklines are explicitly a different, labeled visual series.

## Regression evidence

- `tests/metrics.test.cjs`: cross-year intervals, reversed dates, incomplete prior coverage, no region data, zero revenue.
- `tests/test_controls.py`: forbidden quality failures, expected synthetic exception, unresolved foreign keys, last-good preservation, mock change replay/versioning/reversals/deletes.
- `tests/smoke_pipeline.py`: isolated generation, all four SQLite facts, independent reconciliation, approved export, repeat full rebuild.
- `tests/browser.cjs`: financial filters, currency-versus-unit display, project routes during API failure, keyboard sorting, CSV download, mobile layout, external-CDN fallback.

CI verifies the checked-in public contract and isolates generated smoke-test data in a temporary directory. Both Pages deployment and scheduled refresh depend on successful regression jobs. Refresh additionally gates the newly generated candidate before publishing it.

## Recovery procedure

1. Inspect the failing control and run logs; do not manually change PASS/FAIL fields.
2. Identify source file hashes and use the retained artifact for the last successful run.
3. Correct the generator/adapter/transform, rerun tests, then rerun the complete refresh.
4. Re-run Pages on a verified prior commit if rollback is necessary. A failed candidate never replaces the prior contract.

An exact package lock and input hashes support reproducibility. Timestamps and timing measurements are not expected to be byte-identical. Memory evidence is traced model/export Python allocations, not total process RSS. Multi-user concurrency, throughput under load, and recovery-time objectives are not benchmarked.
