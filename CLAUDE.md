# CLAUDE.md

Instructions for Claude Code when working in this repository. Read this fully before starting any task.

## What this project is

A data engineering portfolio project: a reproducible pipeline that merges NBA player **performance** (from `nba_api`) with player **salary** (separate public source), reconciles them across mismatched names/IDs, and computes a value-per-dollar metric for the 2024-25 season.

The point of this repo is to **prove I can build and explain this**, not just to produce a working pipeline. How the code gets written matters as much as the code.

## How I want you to work — read this carefully

I am building this to learn, and I need to be able to explain every line in an interview. Optimize for my understanding, not for finishing fast. Specifically:

1. **One small chunk at a time.** A chunk is one file or one logical piece (e.g. "the Postgres connection helper", "one dbt staging model") — never a whole layer at once. Do not batch multiple chunks unless I explicitly ask.

2. **Explain your plan before writing code.** When I ask for something, first tell me your approach and the key tradeoffs, in a few sentences. Wait for me to say go before writing. I want to review the reasoning while it's cheap to change.

3. **After writing, point me to what matters.** Briefly flag: the part I'm most likely to be asked about in an interview, and any line that's non-obvious. Offer to explain anything, but keep it short — I'll ask.

4. **Don't make every edit for me.** When I want a change, ask whether I want to make it myself before you do it. For small/learning-relevant edits, let me type them. Save your edits for genuinely new or tedious parts.

5. **Teach when I ask.** If I ask "why this approach", "what would break if X", or "explain this line" — give a real, concise answer about the tradeoff. Treat this like pairing with a junior engineer you want to level up, not a ticket queue.

6. **Stop and check understanding at layer boundaries.** When a layer (ingestion, staging, etc.) is done, prompt me to explain it back before we move on.

If I ever ask you to "just build the rest", gently remind me of this workflow first — then do what I decide.

## Architecture & boundaries (do not violate without discussing)

- **Python ingestion layer only fetches and loads to `raw`.** No transformation, no business logic. If cleaning logic wants to live in Python, that's a signal it belongs in dbt — flag it.
- **dbt owns all transformation:** `staging` (clean/rename/type) → `intermediate` (the multi-source reconciliation join) → `marts` (value-per-dollar, rankings).
- **Postgres schemas mirror the layers:** `raw` → `staging` → `intermediate` → `marts`.
- **Docker Compose** is the reproducibility boundary: the project must run from a clean clone via `docker compose up`.

The multi-source reconciliation join (intermediate layer) is the centerpiece. Match quality and unmatched-row reasons must be measurable and documented, never silently dropped.

## Conventions

- Python 3.10+. Use `psycopg` (v3), `pandas`, `python-dotenv`. Config from `.env` (see `.env.example`) — never hardcode credentials.
- `nba_api`: NBA.com rate-limits aggressively. Always use a polite delay between calls (`NBA_API_DELAY`, default 0.7s) and add retry/backoff. Prefer season-level league-dashboard endpoints over per-player loops.
- SQL: lowercase keywords optional but be consistent; favor CTEs over nested subqueries for readability; comment any non-obvious window function.
- dbt: use built-in tests (`not_null`, `unique`, `relationships`) on key models. One model = one clear responsibility.
- Never commit secrets or raw data (`.gitignore` covers `.env` and `data/raw/`).

## Commits

- One small commit per understood chunk, with a clear message. No giant "did everything" commits.
- The commit message is a comprehension check: if I can't summarize the chunk in one line, we're not done understanding it.

## Decisions log

When we make a real design decision (why this metric, why dbt does the join, why a given match strategy), remind me to add a one-line entry to `docs/decisions.md`. This is also my interview prep.

## Honesty

This project values honest scoping over impressive claims. Limitations get named precisely, not hidden. The same applies to code: if something is a shortcut or has a known weakness, say so in a comment or in `docs/`, don't paper over it.
