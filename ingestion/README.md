# Ingestion layer

Python scripts that pull from each source and land raw data into Postgres.
This layer does **no** transformation — it only fetches, lightly validates,
and loads. All cleaning happens downstream in dbt.

Planned modules:
- `fetch_performance.py` — season player stats via nba_api (league dashboard
  endpoints, with backoff + polite delay for NBA.com rate limits).
- `fetch_salaries.py` — pull the salary dataset for the season.
- `load_raw.py` — load fetched files into the `raw` schema in Postgres.
