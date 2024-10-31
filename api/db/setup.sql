/* The file to setup the flask application database. */

/* The status type of the asset. */
CREATE TYPE ASSET_STATUS_TYPE AS ENUM ('active', 'pending');

/* The table containing information about financial assets. */
CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    status ASSET_STATUS_TYPE NOT NULL DEFAULT 'pending'
);