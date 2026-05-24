# NBA Player Value-Per-Dollar

> Which NBA players gave their teams the most on-court production per dollar of salary in 2024-25 — and which were the most overpaid?

**Status:** 🚧 Work in progress, building in public. The architecture and plan below are firm; implementation is being filled in week by week. See [Build progress](#build-progress).

This is a data engineering project, not just an analysis. The goal is a fully reproducible pipeline that merges two independent data sources (on-court performance and player salaries), reconciles them, and computes a defensible value-per-dollar metric — all runnable from a clean machine with one command.

---

## Why this project

Salary-vs-performance is an intuitive question, but doing it *honestly* is a genuine engineering problem. The two halves of the data live in completely different places:

- **Performance** comes from the official NBA stats API — clean, ID-keyed, advanced metrics included.
- **Salary** comes from a separate public source — different formats, different name spellings, no shared player IDs, and edge cases like mid-season trades and two-way contracts.

Getting those two to agree is the hard, interesting part. The reconciliation join — handling `Nikola Jokić` vs `Nikola Jokic`, traded players, and unmatched rows — is the centerpiece of the project, and its failure cases are documented rather than hidden.

## Architecture

```
  Salary source              NBA Stats API (nba_api)
       │                              │
       └──────────────┬───────────────┘
                      ▼
            Python ingestion layer
       (pull, validate, load to raw — no transforms)
                      ▼
          Postgres · raw schema
        (mirrors source data, untouched)
                      ▼
              dbt transformations
        staging → intermediate → marts
        clean      the join      value/$
                      ▼
       Ranked players + analytical queries
```

| Layer | Tool | Responsibility |
|-------|------|----------------|
| Ingestion | Python | Pull from both sources, validate, land into raw tables. No business logic. |
| Storage | PostgreSQL | Layered schema: `raw` → `staging` → `intermediate` → `marts`. |
| Transformation | dbt | All cleaning, the multi-source join, and the metric. Tested with dbt's built-in tests. |
| Reproducibility | Docker Compose | `docker compose up` brings up Postgres and runs the full pipeline. |

The deliberate boundary — Python *only* ingests, dbt *only* transforms — is a design choice, not an accident.

## The metric

Value-per-dollar for v1 is intentionally simple and fully explainable:

```
value_per_dollar = (single advanced performance metric) / (salary)
```

then normalized and ranked, with an over/underpaid flag relative to expected production at a given salary. The exact performance metric is being finalized (candidates: Win Shares, BPM, VORP — all available from the source).

This is a conscious choice. A blended composite metric is the obvious "next step," but a simple metric I can defend completely in an interview beats a Frankenstein metric I can't. See [Limitations](#limitations).

## Tech stack

- **PostgreSQL** — storage and the analytical SQL layer
- **Python 3.10+** — ingestion (`nba_api`, `requests`, `pandas`, `psycopg`)
- **dbt** — transformations and data tests
- **Docker Compose** — reproducible local environment

## Getting started

> ⚠️ Not yet runnable end-to-end — this section is the target state for Week 1.

```bash
git clone https://github.com/<you>/nba-value-per-dollar.git
cd nba-value-per-dollar
cp .env.example .env        # fill in any config
docker compose up           # brings up Postgres + runs the pipeline
```

## Repo structure

```
nba-value-per-dollar/
├── ingestion/        # Python: pull from sources → load to raw
├── sql/
│   └── queries/      # hand-written analytical queries (window-function showcase)
├── dbt/
│   └── models/
│       ├── staging/        # clean + standardize each source
│       ├── intermediate/   # the multi-source reconciliation join
│       └── marts/          # value-per-dollar, rankings
├── docker/           # Dockerfiles, init scripts
├── docs/             # architecture notes, data-quality reports
├── data/raw/         # gitignored — local landing zone
└── README.md
```

## Build progress

- [ ] **Week 1 — Foundations.** Docker + Postgres up. Python ingestion landing both sources into `raw`. Reproducible from clean clone.
- [ ] **Week 2 — dbt + the join.** Staging models. The reconciliation join in intermediate, with documented match rate and failure cases.
- [ ] **Week 3 — Metric + marts.** Value-per-dollar mart. Analytical queries (rank within position, percentiles, over/underpaid flags).
- [ ] **Week 4 — Polish.** dbt tests, data-quality docs, this README finalized, the honest limitations write-up.

## Limitations

This is a single-season, deliberately-scoped project. Stated plainly because naming limitations precisely is more honest than overclaiming:

- **Single season (2024-25).** No aging curves, no multi-year value, no career-trajectory context.
- **Simple metric.** One performance stat over salary. Ignores positional role, defensive value not captured by the chosen stat, injuries, and minutes context.
- **Salary ≠ cap reality.** Raw salary doesn't account for cap holds, dead money, contract timing, or option years.
- **Reconciliation is imperfect.** Some players won't match cleanly across sources (trades, name variants, two-way deals). The unmatched count and reasons are reported, not hidden.
- **NBA stats API is undocumented.** Endpoints can change without notice; this pull targets a fixed historical season to limit exposure.

### What I'd add with more data / time

Multiple seasons for trend and aging analysis; a blended composite metric with positional adjustment; cap-adjusted salary figures; and porting the analytical queries into a BI layer.

## Data sources & attribution

- Performance: [`nba_api`](https://github.com/swar/nba_api) (official NBA.com stats, MIT-licensed client)
- Salary: public salary dataset (source finalized in Week 1)

This project is for educational and portfolio purposes. NBA.com data is subject to the [NBA.com Terms of Use](https://www.nba.com/termsofuse).

## License

MIT — see [LICENSE](LICENSE).
