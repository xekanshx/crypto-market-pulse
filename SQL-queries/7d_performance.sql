SELECT coin_id AS coin_id,
       window_start AS window_start,
       pct_change_7d AS pct_change_7d,
       performance_label AS performance_label
FROM
  (WITH weekly_performance AS
     (SELECT coin_id,
             fetch_date,
             current_price,
             LEAD(current_price, 7) OVER (PARTITION BY coin_id
                                          ORDER BY fetch_date) AS price_7days_later,
                                         ROUND(((LEAD(current_price, 7) OVER (PARTITION BY coin_id
                                                                              ORDER BY fetch_date) - current_price) / NULLIF(current_price, 0) * 100)::NUMERIC, 2) AS pct_change_7d
      FROM crypto_prices
      WHERE coin_id NOT IN ('tether',
                            'usd-coin',
                            'usds',
                            'canton-network',
                            'lab') ),
        ranked AS
     (SELECT *,
             RANK() OVER (PARTITION BY coin_id
                          ORDER BY pct_change_7d DESC) AS best_rank,
                         RANK() OVER (PARTITION BY coin_id
                                      ORDER BY pct_change_7d ASC) AS worst_rank
      FROM weekly_performance
      WHERE pct_change_7d IS NOT NULL ) SELECT coin_id,
                                               fetch_date AS window_start,
                                               pct_change_7d,
                                               CASE
                                                   WHEN best_rank = 1 THEN 'Best 7-day window'
                                                   WHEN worst_rank = 1 THEN 'Worst 7-day window'
                                               END AS performance_label
   FROM ranked
   WHERE best_rank = 1
     OR worst_rank = 1
   ORDER BY coin_id,
            pct_change_7d DESC) AS virtual_table
ORDER BY pct_change_7d DESC
LIMIT 50;
