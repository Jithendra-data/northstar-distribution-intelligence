# ERP integration contract — tested mock, not a live connector

## Example domain: posted invoice changes

| Contract field | Meaning |
|---|---|
| source, legal_entity, invoice_id, line | Stable composite identity; business units cannot collide |
| version | Monotonically increasing source change version for this line |
| revenue_cents | Signed integer USD amount; a reversal may be negative |
| currency, uom | USD and EA in the mock; unsupported values rejected |
| operation | upsert or delete (tombstone) |

Example event:
```json
{"source":"mock","legal_entity":"US01","invoice_id":"INV1","line":1,"version":3,"revenue_cents":12345,"currency":"USD","uom":"EA","operation":"upsert"}
```

`etl/mock_erp_adapter.py` and its regression test implement idempotent replay, version ordering, same-version payload-conflict rejection, signed corrections, deletion tombstones, and atomic batch rollback. This adapter is a standalone contract demonstration, not connected to the production synthetic runner or a real ERP API.

## Proposed real extraction boundary

Select a supported source API/export for invoice headers and lines. Capture a committed extraction watermark only after the sink transaction and control totals succeed. Persist source event/version identifiers; retry the same batch safely. A delete remains a tombstone to prevent a late historical event resurrecting it. Establish source-specific cancellation, credit-note, timezone, fiscal period, currency, and unit conversion mappings before implementation.

Master data: customer, product, warehouse, vendor and legal entity require assigned owners and durable cross-system mappings. Customer/Product keys must resolve before fact acceptance. Unknown-member and SCD Type 2 handling are design decisions still to implement for a real deployment.

Finance approval: reconcile header/line totals, credit notes, tax/freight treatment, currency, posting statuses, and source batch totals. Synthetic gross profit uses generated costs and is not a general-ledger integration. Vendor fill rate is not OTIF; receipt quantity alone cannot establish on-time-in-full at an agreed delivery grain.

Credential plan: secret manager, least-privilege read-only extraction identity, rotation, and environment separation. No real ERP credentials or endpoints are included. Acceptance requires source-owner signoff plus repeat/recovery and reconciliation tests against a representative authorized extract.
