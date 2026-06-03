SELECT DATE_TRUNC('day', fetch_date) AS fetch_date,
       coin_id AS coin_id,
       AVG(normalized_30day_avg) AS "AVG(normalized_30day_avg)"
FROM
  (WITH price_stats AS
     (SELECT coin_id,
             fetch_date,
             current_price,
             MIN(current_price) OVER (PARTITION BY coin_id) AS min_price,
                                     MAX(current_price) OVER (PARTITION BY coin_id) AS max_price,
                                                             AVG(current_price) OVER (PARTITION BY coin_id
                                                                                      ORDER BY fetch_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS rolling_30day_avg
      FROM crypto_prices
      WHERE coin_id IN ('bitcoin',
                        'ethereum',
                        'solana',
                        'dogecoin',
                        'binancecoin') ) SELECT coin_id,
                                                fetch_date,
                                                ROUND(((current_price - min_price) / NULLIF(max_price - min_price, 0) * 100)::NUMERIC, 2) AS normalized_price,
                                                ROUND(((rolling_30day_avg - min_price) / NULLIF(max_price - min_price, 0) * 100)::NUMERIC, 2) AS normalized_30day_avg
   FROM price_stats
   ORDER BY coin_id,
            fetch_date) AS virtual_table
GROUP BY DATE_TRUNC('day', fetch_date),
         coin_id
ORDER BY "AVG(normalized_30day_avg)" DESC
LIMIT 1000;
