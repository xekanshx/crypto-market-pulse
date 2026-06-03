import logging
import os
import time
from datetime import datetime, timedelta, timezone

import psycopg2
import requests
from psycopg2.extras import execute_values
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "user": os.getenv("DB_USER", "crypto_user"),
    "password": os.getenv("DB_PASSWORD", "crypto_pass"),
    "dbname": os.getenv("DB_NAME", "crypto_data"),
    "port": int(os.getenv("DB_PORT", "5432")),
}

VS_CURRENCY = os.getenv("VS_CURRENCY", "usd")
PER_PAGE = int(os.getenv("TOP_COINS_LIMIT", "20"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
BACKFILL_DAYS = 365


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def get_session():
    retry = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def fetch_top_coin_ids(session) -> list:
    """Fetch the same top N coins your daily script uses."""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": VS_CURRENCY,
        "order": "market_cap_desc",
        "per_page": PER_PAGE,
        "page": 1,
        "sparkline": "false",
    }
    response = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    coins = response.json()
    return [c["id"] for c in coins if c.get("id")]


def fetch_market_chart(session, coin_id: str, from_ts: int, to_ts: int) -> list:
    """
    Returns daily data points as list of (date, price, market_cap, volume).
    CoinGecko returns daily granularity automatically for ranges > 90 days.
    """
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"
    params = {
        "vs_currency": VS_CURRENCY,
        "from": from_ts,
        "to": to_ts,
    }
    response = session.get(url, params=params, timeout=REQUEST_TIMEOUT)

    if response.status_code == 429:
        logger.warning("Rate limited on %s, sleeping 60s...", coin_id)
        time.sleep(60)
        response = session.get(url, params=params, timeout=REQUEST_TIMEOUT)

    response.raise_for_status()
    data = response.json()

    prices = {ts: p for ts, p in data.get("prices", [])}
    market_caps = {ts: m for ts, m in data.get("market_caps", [])}
    volumes = {ts: v for ts, v in data.get("total_volumes", [])}

    rows = []
    for ts_ms, price in prices.items():
        dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
        rows.append((
            dt.date(),
            dt,
            price,
            market_caps.get(ts_ms),
            volumes.get(ts_ms),
        ))

    return rows


def get_existing_dates(coin_id: str) -> set:
    """Skip dates we already have to make the backfill safe to re-run."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT fetch_date FROM crypto_prices WHERE coin_id = %s",
                (coin_id,)
            )
            return {row[0] for row in cur.fetchall()}


def insert_historical_rows(coin_id: str, coin_rows: list) -> None:
    insert_sql = """
    INSERT INTO crypto_prices (
        fetch_date, fetched_at, coin_id,
        current_price, market_cap, total_volume
    ) VALUES %s
    ON CONFLICT (fetch_date, coin_id) DO NOTHING;
    """
    # DO NOTHING so we never overwrite data your daily script already stored

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            execute_values(cur, insert_sql, coin_rows)
        conn.commit()

    logger.info("Inserted %s rows for %s", len(coin_rows), coin_id)


def backfill():
    session = get_session()

    logger.info("Fetching top %s coins...", PER_PAGE)
    coin_ids = fetch_top_coin_ids(session)
    logger.info("Coins to backfill: %s", coin_ids)
    time.sleep(2)

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=BACKFILL_DAYS)
    from_ts = int(start.timestamp())
    to_ts = int(end.timestamp())

    for i, coin_id in enumerate(coin_ids, 1):
        logger.info("[%s/%s] Backfilling %s...", i, len(coin_ids), coin_id)

        existing_dates = get_existing_dates(coin_id)

        try:
            rows = fetch_market_chart(session, coin_id, from_ts, to_ts)
        except requests.RequestException as exc:
            logger.error("Failed to fetch %s: %s — skipping", coin_id, exc)
            time.sleep(5)
            continue

        # Filter out dates we already have
        new_rows = [
            (fetch_date, fetched_at, coin_id, price, market_cap, volume)
            for fetch_date, fetched_at, price, market_cap, volume in rows
            if fetch_date not in existing_dates
        ]

        if new_rows:
            insert_historical_rows(coin_id, new_rows)
        else:
            logger.info("No new rows for %s, already up to date", coin_id)

        # Be polite to the free tier — 2s between each coin
        time.sleep(2)

    logger.info("Backfill complete!")


if __name__ == "__main__":
    backfill()
