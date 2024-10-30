/* The file to setup the flask application database. */

/* The table containing information about financial assets. */
CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);