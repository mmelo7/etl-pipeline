CREATE TABLE IF NOT EXISTS crypto_prices (
    id SERIAL PRIMARY KEY,
    currency VARCHAR(50),
    price_usd FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);