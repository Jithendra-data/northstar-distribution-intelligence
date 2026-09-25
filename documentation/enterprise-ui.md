# Enterprise UI refinement

## Executive product polish

The overview now places KPI cards and five ranked Executive Signals ahead of technical material. Resource links live with Project Story. Every card has a definition and a mini-chart: monthly series where available, or an explicitly labeled single snapshot when historical customer, inventory, or purchase commitment values are absent. Monthly revenue YoY sparklines preserve gaps where prior-year values are unavailable. Existing KPI calculations remain unchanged.

Signals are recomputed from each published dataset using deterministic triage scores. Inventory exposure, supplier deterioration, customer inactivity, warehouse service gaps, purchasing commitments, and margin movement compete for five positions. The UI explains the ranking and full-dataset scope. Detailed observations remain available below the core charts.

Architecture provides seven selectable lineage stages with keyboard controls and implementation links. It distinguishes logical SQL warehouse design from the active Python/CSV pipeline, including the analytics builder's direct raw-extract inputs. No live database connection is implied.

Polish verification: eight mini-charts, three snapshot disclosures, five signals, seven lineage stages, keyboard stage selection, region and date filtering, both ECharts charts, and empty search states passed. Layouts at 390, 768, 1024, and 1440 pixels had no page overflow; no JavaScript errors were observed.

The existing application is static HTML, CSS, and JavaScript backed by the pipeline's dashboard JSON export. Inspection found that the project narrative preceded operational metrics, filters crowded the heading, card styles competed for emphasis, and sortable headers lacked keyboard controls.

The update puts analytics first and retains the entire project narrative below the operational sections. The filter toolbar explains scope; monthly comparisons are computed from the last two selected observations, while customer, inventory, and purchase commitment cards explicitly retain full dataset scope. No pipeline, export schema, or existing KPI formula was changed.

Design references:

- [shadcn/ui theming](https://ui.shadcn.com/docs/theming): semantic surface, foreground, border, primary, and focus tokens in `web/css/enterprise.css` form the visual foundation for native cards, buttons, badges, and tables.
- [Magic UI](https://magicui.design/docs/components/border-beam) and [Aceternity cards](https://ui.aceternity.com/blocks/cards): restrained border emphasis and card interaction references. React component packages were not added to this static application.
- Existing GSAP handles a short entrance transition. Reduced motion disables it and chart animations. CSS handles hover and loading states.

Verification completed in headless Edge: both ECharts charts, region and date changes, keyboard sorting, table search and empty state, CSV download, pagination, section navigation, reduced motion, and layouts at 390, 768, 1024, and 1440 pixels. No JavaScript errors or page horizontal overflow were observed. CDN failure was also exercised: both SVG fallback charts rendered. Screenshot captures are in `screenshots/enterprise-desktop.png` and `screenshots/enterprise-mobile.png`. JavaScript syntax, dashboard JSON parsing, and Git whitespace checks passed.
