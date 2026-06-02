import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

import psycopg2
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from psycopg2.extras import execute_values
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "user": os.getenv("DB_USER", "crypto_user"),
    "password": os.getenv("DB_PASSWORD", "crypto_pass"),
    "dbname": os.getenv("DB_NAME", "crypto_data"),
    "port": int(os.getenv("DB_PORT", "5432")),
}

VS_CURRENCY = os.getenv("VS_CURRENCY", "usd")
PER_PAGE = int(os.getenv("TOP_COINS_LIMIT", "20"))
SCHEDULE_HOUR = int(os.getenv("FETCH_HOUR", "0"))
SCHEDULE_MINUTE = int(os.getenv("FETCH_MINUTE", "5"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def ensure_table() -> None:
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS crypto_prices (
        id SERIAL PRIMARY KEY,
        fetch_date DATE NOT NULL,
        fetched_at TIMESTAMPTZ NOT NULL,
        coin_id TEXT NOT NULL,
        symbol TEXT,
        name TEXT,
        current_price NUMERIC,
        market_cap NUMERIC,
        total_volume NUMERIC,
        price_change_percentage_24h NUMERIC,
        market_cap_rank INTEGER,
        high_24h NUMERIC,
        low_24h NUMERIC,
        circulating_supply NUMERIC,
        total_supply NUMERIC,
        max_supply NUMERIC,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        UNIQUE(fetch_date, coin_id)
    );
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(create_table_sql)
        conn.commit()


def fetch_crypto_data() -> List[Dict[str, Any]]:
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))

    params = {
        "vs_currency": VS_CURRENCY,
        "order": "market_cap_desc",
        "per_page": PER_PAGE,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h",
    }
    response = session.get(COINGECKO_URL, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, list):
        raise ValueError("Unexpected API response format from CoinGecko")
    return data


def insert_crypto_data(data: List[Dict[str, Any]]) -> None:
    now = datetime.now(timezone.utc)
    fetch_date = now.date()

    insert_sql = """
    INSERT INTO crypto_prices (
        fetch_date,
        fetched_at,
        coin_id,
        symbol,
        name,
        current_price,
        market_cap,
        total_volume,
        price_change_percentage_24h,
        market_cap_rank,
        high_24h,
        low_24h,
        circulating_supply,
        total_supply,
        max_supply
    ) VALUES %s
    ON CONFLICT (fetch_date, coin_id) DO UPDATE SET
        fetched_at = EXCLUDED.fetched_at,
        symbol = EXCLUDED.symbol,
        name = EXCLUDED.name,
        current_price = EXCLUDED.current_price,
        market_cap = EXCLUDED.market_cap,
        total_volume = EXCLUDED.total_volume,
        price_change_percentage_24h = EXCLUDED.price_change_percentage_24h,
        market_cap_rank = EXCLUDED.market_cap_rank,
        high_24h = EXCLUDED.high_24h,
        low_24h = EXCLUDED.low_24h,
        circulating_supply = EXCLUDED.circulating_supply,
        total_supply = EXCLUDED.total_supply,
        max_supply = EXCLUDED.max_supply;
    """

    rows = [
        (
            fetch_date,
            now,
            coin.get("id"),
            coin.get("symbol"),
            coin.get("name"),
            coin.get("current_price"),
            coin.get("market_cap"),
            coin.get("total_volume"),
            coin.get("price_change_percentage_24h"),
            coin.get("market_cap_rank"),
            coin.get("high_24h"),
            coin.get("low_24h"),
            coin.get("circulating_supply"),
            coin.get("total_supply"),
            coin.get("max_supply"),
        )
        for coin in data
        if coin.get("id")
    ]

    if not rows:
        logger.warning("No valid coin rows received; skipping insert")
        return

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            execute_values(cur, insert_sql, rows)
        conn.commit()

    logger.info("Stored %s crypto records for %s", len(rows), fetch_date)


def run_fetch_job() -> None:
    logger.info("Starting daily CoinGecko fetch job")
    try:
        ensure_table()
        data = fetch_crypto_data()
        insert_crypto_data(data)
        logger.info("Fetch job completed successfully")
    except requests.RequestException as exc:
        logger.exception("HTTP error fetching CoinGecko data: %s", exc)
    except psycopg2.Error as exc:
        logger.exception("Database error while storing crypto data: %s", exc)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error in fetch job: %s", exc)


def main() -> None:
    logger.info(
        "Crypto fetcher started: db=%s@%s:%s, schedule=%02d:%02d UTC",
        DB_CONFIG["dbname"],
        DB_CONFIG["host"],
        DB_CONFIG["port"],
        SCHEDULE_HOUR,
        SCHEDULE_MINUTE,
    )

    run_fetch_job()

    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(run_fetch_job, "cron", hour=SCHEDULE_HOUR, minute=SCHEDULE_MINUTE)

    logger.info("Scheduler running in foreground")
    scheduler.start()


if __name__ == "__main__":
    main()
