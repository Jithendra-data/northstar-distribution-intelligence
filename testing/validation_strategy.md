# Validation Strategy

Run deterministic generation, key/relationship checks, domain checks, transaction-to-fact transformations, and raw-to-mart reconciliation. Quality tests report denominator and failed row count. Intentional exceptions should be visible and classified, not mistaken for clean source data. Reconciliation tolerances are zero for copied additive monetary/quantity measures, with rounding tolerance documented for derived values.

