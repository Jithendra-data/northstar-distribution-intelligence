# Private deployment and enterprise-scale design

## Public boundary

The current static site contains synthetic records. It is intentionally unauthenticated. The reference database and raw extracts are not deployed with `web/`. Publishing confidential data to this deployment is unsupported.

## Proposed private boundary (not implemented)

Corporate identity provider → authenticated application/API → authorization-enforced warehouse queries. Apply tenant/legal-entity/region controls in the service and database rather than hiding rows in JavaScript. Use separate ingestion and query identities, least privilege, encrypted transport/storage, secret rotation, data retention rules, and auditable access logs. Classify PII and minimize names/addresses in analytical exports. Approve threat model and restore drills before a pilot with real data.

## Scale triggers

Measure row counts, pipeline time, total process memory, browser payload, parsing time, and query latency before adding infrastructure. The present manifest measures input hashes, fact row counts, total processing time, and traced model/export Python allocation peak. It is not a load benchmark.

For larger datasets: partition staging, move persisted facts to a managed database, implement incremental extraction and replay, add effective-dated dimensions, serve authorized paginated drill-through, and split overview summaries from detail payloads. Define an agreed payload/performance budget based on target devices and network conditions. No concurrency or availability SLA is currently demonstrated.

## Governance to establish with an enterprise customer

Metric owner, approved definition and version, lineage owner, data steward, control severity/tolerance, exception expiry, freshness objective, access matrix, retention policy, and change approval. The demo's descriptive lineage and metric dictionary are evidence of intent, not an enterprise catalog or governance program.
