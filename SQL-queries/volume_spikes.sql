WITH daily_avg AS (
    SELECT
        coin_id,
        fetch_date,
        total_volume,
        AVG(total_volume) OVER (
            PARTITION BY coin_id
            ORDER BY fetch_date
            ROWS BETWEEN 30 PRECEDING AND 1 PRECEDING
        ) AS avg_30day_volume
    FROM crypto_prices
    WHERE coin_id NOT IN ('tether', 'usd-coin', 'usds')
)
SELECT
    coin_id,
    fetch_date,
    ROUND(total_volume::NUMERIC, 2) AS volume,
    ROUND(avg_30day_volume::NUMERIC, 2) AS avg_30day_volume,
    ROUND((total_volume / avg_30day_volume)::NUMERIC, 2) AS volume_spike_ratio
FROM daily_avg
WHERE total_volume > 2 * avg_30day_volume
ORDER BY volume_spike_ratio DESC;
