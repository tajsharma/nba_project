import os
import time
import pandas as pd
from dotenv import load_dotenv
from nba_api.stats.endpoints import LeagueDashPlayerStats
from ingestion.db import get_connection

load_dotenv()

NBA_API_DELAY = float(os.getenv("NBA_API_DELAY", "0.7"))
MAX_RETRIES = 3


def fetch_player_stats(season: str = "2024-25") -> pd.DataFrame:
    last_exc = None
    for attempt in range(MAX_RETRIES):
        try:
            result = LeagueDashPlayerStats(
                season=season,
                season_type_all_star="Regular Season",
            )
            time.sleep(NBA_API_DELAY)
            return result.get_data_frames()[0]
        except Exception as exc:
            last_exc = exc
            print(f"Attempt {attempt + 1} failed: {exc}. Retrying...")
            time.sleep(NBA_API_DELAY * 2)
    raise last_exc


def load_to_postgres(df: pd.DataFrame, season: str = "2024-25") -> None:
    # lowercase column names so SQL stays clean
    df.columns = [c.lower() for c in df.columns]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS raw.player_stats (
                    player_id           INTEGER,
                    player_name         TEXT,
                    team_id             INTEGER,
                    team_abbreviation   TEXT,
                    gp                  INTEGER,
                    min                 NUMERIC,
                    pts                 NUMERIC,
                    reb                 NUMERIC,
                    ast                 NUMERIC,
                    season              TEXT,
                    PRIMARY KEY (player_id, season)
                )
            """)

            rows = [
                (
                    row["player_id"],
                    row["player_name"],
                    row["team_id"],
                    row["team_abbreviation"],
                    row["gp"],
                    row["min"],
                    row["pts"],
                    row["reb"],
                    row["ast"],
                    season,
                )
                for _, row in df.iterrows()
            ]

            cur.executemany("""
                INSERT INTO raw.player_stats
                    (player_id, player_name, team_id, team_abbreviation,
                     gp, min, pts, reb, ast, season)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (player_id, season) DO NOTHING
            """, rows)

        conn.commit()


if __name__ == "__main__":
    print("Fetching 2024-25 player stats...")
    df = fetch_player_stats()
    print(f"Fetched {len(df)} rows.")
    load_to_postgres(df)
    print("Loaded into raw.player_stats.")
