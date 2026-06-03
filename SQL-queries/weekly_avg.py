WITH daily_volume AS (
    SELECT
        fetch_date,
        coin_id,
        total_volume,
        AVG(total_volume) OVER (
            PARTITION BY coin_id
            ORDER BY fetch_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS volume_7day_avg
    FROM crypto_prices
),
latest AS (
    SELECT
        coin_id,
        volume_7day_avg AS latest_7day_avg_volume
    FROM daily_volume
    WHERE fetch_date = (SELECT MAX(fetch_date) FROM crypto_prices)
)
SELECT
    coin_id,
    ROUND(latest_7day_avg_volume::NUMERIC, 2) AS avg_7day_volume
FROM latest
ORDER BY avg_7day_volume DESC
LIMIT 10;
