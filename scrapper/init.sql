CREATE DATABASE racing_db;

\c racing_db

CREATE TABLE example_table (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);
