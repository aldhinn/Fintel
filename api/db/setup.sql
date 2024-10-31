/* The file to setup the flask application database. */

/* The status type of the ticker. */
CREATE TYPE TICKER_STATUS_TYPE AS ENUM ('active', 'pending');

/* The table containing information about financial tickers. */
CREATE TABLE IF NOT EXISTS tickers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    status TICKER_STATUS_TYPE NOT NULL DEFAULT 'pending'
);