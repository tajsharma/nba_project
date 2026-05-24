# Decisions log

One line per real design decision, written while the reasoning is fresh.
Doubles as interview prep — when asked "why'd you build it this way", read from here.

| Date | Decision | Why |
|------|----------|-----|
| 2026-05 | Two data sources: nba_api (performance) + separate salary source | NBA.com publishes no salary data; the merge is the project's core engineering challenge, not a limitation. |
| 2026-05 | Python ingests, dbt transforms — hard boundary | Mirrors modern-data-stack norms; keeps each tool doing one job; easier to explain. |
| 2026-05 | Single, explainable performance metric over a blended composite (v1) | A metric I can fully defend beats a Frankenstein metric I can't. |
