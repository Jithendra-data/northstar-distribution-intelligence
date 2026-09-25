# Investigation: inventory exposure and service decisions

## Problem and owner

A distribution planning lead needs to identify stock with no recent movement, while procurement reviews overdue inbound commitments and finance challenges the valuation. NorthStar provides a repeatable evidence path using synthetic records. No operational intervention or realized savings is claimed.

## Reproduce the observation

Run the pipeline, open Executive Signals, select Inventory exposure, and inspect the dedicated affected-position extract. The predicate is positive AvailableQty and zero Sales90Day, valued as AvailableQty × current Product.UnitCost. The displayed queue is capped at 500 rows; its eligible population and selection rule are disclosed. The full-dataset amount is calculated before capping.

Compare positive inventory, the negative-stock adjustment, and net inventory. Do not infer that negative positions are a subset of a velocity-based Critical category: the two predicates can overlap differently, especially when velocity is zero.

## Alternative explanations

No recent shipments does not prove obsolescence. Seasonality, safety stock, new products, incorrect source movements, or pending demand could explain it. Current unit cost is a demonstration valuation policy, not an approved accounting method. Net value can conceal negative positions, so the dashboard shows them separately.

## Decision and verification plan

Inventory Planning reviews the queue, confirms physical and demand evidence, and approves replenishment holds or disposition. Procurement reconciles inbound commitments before cancelling anything. Finance approves recovery assumptions. The signal is resolved when each selected position has an agreed action and owner—not merely when its record disappears from the dashboard.

Pilot measures: analyst preparation time before/after, validated candidate stock, disposition cost, realized proceeds, stockout impact, and repeat exceptions. No baseline or outcomes have been measured with a real business, so none are invented.

## Measured technical results

Use the live Project & Architecture Results section or `web/data/dashboard.json` for the current publication's fact counts, runtime, dependencies, hashes, and control results. Five measures reconcile raw sources to executed SQLite facts and dashboard values. The pipeline uses normalized staging for transformations and retains the prior public dataset on candidate failure.

## Modeled opportunity, not outcome

The interactive value model asks for disposition share, annual carrying-cost rate, and attainable margin points. It clearly separates annual carrying-cost opportunity from margin opportunity on the selected full historical dataset. They have different time bases and are not added into ROI. Real implementation cost, labor baseline, feasibility, and sustained benefits remain to validate.
