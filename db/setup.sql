/* The file to setup the flask application database. */

/* The table containing currencies. */
CREATE TABLE IF NOT EXISTS currencies (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    description VARCHAR(50)
);

/* Populate currencies table with popular currencies. */
INSERT INTO currencies (symbol, description) VALUES
    ('USD', 'US Dollar'),
    ('EUR', 'Euro'),
    ('JPY', 'Japanese Yen'),
    ('GBP', 'British Pound'),
    ('AUD', 'Australian Dollar'),
    ('CAD', 'Canadian Dollar'),
    ('CHF', 'Swiss Franc'),
    ('CNY', 'Chinese Yuan Renminbi'),
    ('NZD', 'New Zealand Dollar'),
    ('SEK', 'Swedish Krona'),
    ('NOK', 'Norwegian Krone'),
    ('MXN', 'Mexican Peso'),
    ('SGD', 'Singapore Dollar'),
    ('HKD', 'Hong Kong Dollar'),
    ('KRW', 'South Korean Won'),
    ('TRY', 'Turkish Lira'),
    ('INR', 'Indian Rupee'),
    ('RUB', 'Russian Ruble'),
    ('ZAR', 'South African Rand'),
    ('BRL', 'Brazilian Real'),
    ('PHP', 'Philippine Peso'),
    ('SAR', 'Saudi Riyal');

/* Type describing the processing status of the asset. */
CREATE TYPE asset_status_type AS ENUM ('active', 'pending');
/* Type describing the category of the asset */
CREATE TYPE asset_category_type AS ENUM ('stock', 'bond', 'forex', 'crypto');
/* Type describing the source of data. */
CREATE TYPE data_source_type AS ENUM ('yahoo_finance', 'alpha_vantage');

/* The table containing information about financial assets. */
CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(15) UNIQUE NOT NULL,
    description VARCHAR(50),
    processing_status asset_status_type NOT NULL DEFAULT 'pending',
    category asset_category_type,
    currency_medium VARCHAR(10) REFERENCES currencies(symbol) -- The currency medium this asset is being exchanged with.
);

/* The table containing information about asset price points. */
CREATE TABLE IF NOT EXISTS price_points (
    id SERIAL PRIMARY KEY,

    /* If an asset entry is deleted, every price point entry
    relating to that asset is to be deleted.*/
    asset_id INT REFERENCES assets(id) ON DELETE CASCADE,

    date DATE NOT NULL,
    open_price NUMERIC(12, 4) NOT NULL,
    close_price NUMERIC(12, 4) NOT NULL,
    high_price NUMERIC(12, 4) NOT NULL,
    low_price NUMERIC(12, 4) NOT NULL,
    adjusted_close NUMERIC(12, 4),
    volume BIGINT,
    source data_source_type NOT NULL,
    UNIQUE (asset_id, date, source)
);

/* Table containing model data. */
CREATE TABLE ai_models (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL UNIQUE,
    model_type VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_data BYTEA NOT NULL,
    last_trained TIMESTAMP
);

-- Define an ENUM type with only the allowed prediction types.
CREATE TYPE prediction_type_enum AS ENUM ('open_price', 'high_price', 'low_price', 'close_price', 'adjusted_close', 'volume');

-- Create the predictions table with the ENUM type constraint.
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    model_id INTEGER NOT NULL REFERENCES ai_models(id) ON DELETE CASCADE,
    prediction_type prediction_type_enum NOT NULL,
    prediction NUMERIC NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    retrained BOOLEAN DEFAULT FALSE
);