SELECT
    coin_id,
    ROUND(STDDEV(current_price)::NUMERIC, 2) AS price_volatility,
    ROUND(AVG(current_price)::NUMERIC, 2) AS avg_price,
    ROUND((STDDEV(current_price) / AVG(current_price) * 100)::NUMERIC, 2) AS volatility_pct
FROM crypto_prices
WHERE fetch_date >= CURRENT_DATE - INTERVAL '90 days'
AND coin_id NOT IN ('tether', 'usd-coin', 'usds')
GROUP BY coin_id
ORDER BY volatility_pct DESC;
