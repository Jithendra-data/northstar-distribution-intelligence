# Enterprise UI refinement

The existing application is static HTML, CSS, and JavaScript backed by the pipeline's dashboard JSON export. Inspection found that the project narrative preceded operational metrics, filters crowded the heading, card styles competed for emphasis, and sortable headers lacked keyboard controls.

The update puts analytics first and retains the entire project narrative below the operational sections. The filter toolbar explains scope; monthly comparisons are computed from the last two selected observations, while customer, inventory, and purchase commitment cards explicitly retain full dataset scope. No pipeline, export schema, or existing KPI formula was changed.

Design references:

- [shadcn/ui theming](https://ui.shadcn.com/docs/theming): semantic surface, foreground, border, primary, and focus tokens in `web/css/enterprise.css` form the visual foundation for native cards, buttons, badges, and tables.
- [Magic UI](https://magicui.design/docs/components/border-beam) and [Aceternity cards](https://ui.aceternity.com/blocks/cards): restrained border emphasis and card interaction references. React component packages were not added to this static application.
- Existing GSAP handles a short entrance transition. Reduced motion disables it and chart animations. CSS handles hover and loading states.

Verification completed in headless Edge: both ECharts charts, region and date changes, keyboard sorting, table search and empty state, CSV download, pagination, section navigation, reduced motion, and layouts at 390, 768, 1024, and 1440 pixels. No JavaScript errors or page horizontal overflow were observed. CDN failure was also exercised: both SVG fallback charts rendered. Screenshot captures are in `screenshots/enterprise-desktop.png` and `screenshots/enterprise-mobile.png`. JavaScript syntax, dashboard JSON parsing, and Git whitespace checks passed.
