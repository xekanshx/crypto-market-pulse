SELECT coin_id AS coin_id,
       latest_price AS latest_price,
       pct_change_7d AS pct_change_7d,
       pct_change_30d AS pct_change_30d
FROM
  (WITH latest_date AS
     (SELECT MAX(fetch_date) AS max_date
      FROM crypto_prices),
        price_points AS
     (SELECT cp.coin_id,
             cp.current_price AS latest_price,
             p7.current_price AS price_7d_ago,
             p30.current_price AS price_30d_ago
      FROM crypto_prices cp
      JOIN latest_date ld ON cp.fetch_date = ld.max_date
      LEFT JOIN crypto_prices p7 ON p7.coin_id = cp.coin_id
      AND p7.fetch_date = ld.max_date - INTERVAL '7 days'
      LEFT JOIN crypto_prices p30 ON p30.coin_id = cp.coin_id
      AND p30.fetch_date = ld.max_date - INTERVAL '30 days'
      WHERE cp.coin_id NOT IN ('tether',
                               'usd-coin',
                               'usds',
                               'canton-network',
                               'lab') ) SELECT coin_id,
                                               ROUND(latest_price::NUMERIC, 4) AS latest_price,
                                               ROUND(((latest_price - price_7d_ago) / NULLIF(price_7d_ago, 0) * 100)::NUMERIC, 2) AS pct_change_7d,
                                               ROUND(((latest_price - price_30d_ago) / NULLIF(price_30d_ago, 0) * 100)::NUMERIC, 2) AS pct_change_30d
   FROM price_points
   ORDER BY pct_change_7d DESC) AS virtual_table
ORDER BY pct_change_7d DESC
LIMIT 1000;
