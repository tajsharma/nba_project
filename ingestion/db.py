import os
from dotenv import load_dotenv
import psycopg

load_dotenv()


def get_connection() -> psycopg.Connection:
    """Return a psycopg v3 connection using credentials from .env."""
    return psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )
