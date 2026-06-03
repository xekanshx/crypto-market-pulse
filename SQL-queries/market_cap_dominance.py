SELECT DATE_TRUNC('day', month) AS month,
       coin_id AS coin_id,
       AVG(dominance_pct) AS "AVG(dominance_pct)"
FROM
  (SELECT coin_id,
          DATE_TRUNC('month', fetch_date) AS month,
          ROUND(AVG(market_cap)::NUMERIC, 2) AS avg_monthly_market_cap,
          ROUND((AVG(market_cap) / SUM(AVG(market_cap)) OVER (PARTITION BY DATE_TRUNC('month', fetch_date)) * 100)::NUMERIC, 2) AS dominance_pct
   FROM crypto_prices
   WHERE coin_id NOT IN ('tether',
                         'usd-coin',
                         'usds')
     AND market_cap IS NOT NULL
   GROUP BY coin_id,
            DATE_TRUNC('month', fetch_date)
   ORDER BY month,
            dominance_pct DESC) AS virtual_table
JOIN
  (SELECT coin_id AS coin_id__,
          AVG(dominance_pct) AS mme_inner__
   FROM
     (SELECT coin_id,
             DATE_TRUNC('month', fetch_date) AS month,
             ROUND(AVG(market_cap)::NUMERIC, 2) AS avg_monthly_market_cap,
             ROUND((AVG(market_cap) / SUM(AVG(market_cap)) OVER (PARTITION BY DATE_TRUNC('month', fetch_date)) * 100)::NUMERIC, 2) AS dominance_pct
      FROM crypto_prices
      WHERE coin_id NOT IN ('tether',
                            'usd-coin',
                            'usds')
        AND market_cap IS NOT NULL
      GROUP BY coin_id,
               DATE_TRUNC('month', fetch_date)
      ORDER BY month,
               dominance_pct DESC) AS virtual_table
   GROUP BY coin_id
   ORDER BY AVG(dominance_pct) DESC
   LIMIT 5) AS series_limit ON coin_id = coin_id__
GROUP BY DATE_TRUNC('day', month),
         coin_id
ORDER BY "AVG(dominance_pct)" DESC
LIMIT 100;
