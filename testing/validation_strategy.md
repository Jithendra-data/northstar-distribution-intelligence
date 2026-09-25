# Validation strategy

Run Python unit tests, pure-JavaScript metric tests, isolated full-pipeline replay, and persistent browser regression before deployment. The published contract itself must pass the publication validator. Smoke tests never overwrite the checked-in public dataset.

Mandatory failures block publication: unexpected source checks, PK/FK resolution, missing/nonfinite contract measures, or any of five reconciliation failures. The only allowed synthetic exception is Negative ending on-hand; it is explicitly labeled EXPECTED_SCENARIO. A real ERP ingestion policy does not inherit that exception.

Tests and evidence: see documentation/engineering/decisions.md. No claim is made that these tests establish comprehensive security, accessibility conformance, finance certification, or enterprise-scale performance.
