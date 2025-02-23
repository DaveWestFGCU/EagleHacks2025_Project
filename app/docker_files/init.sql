-- Ensure database exists
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'eaglehacks_2025') THEN
        CREATE DATABASE eaglehacks_2025;
    END IF;
END $$;

-- Ensure user exists
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'eaglehacks_2025') THEN
        CREATE USER eaglehacks_2025 WITH PASSWORD 'password';
    END IF;
END $$;

GRANT ALL PRIVILEGES ON DATABASE eaglehacks_2025 TO eaglehacks_2025;

-- Connect to the database
\c eaglehacks_2025;

-- Create the users table if it doesn't exist
-- Create the users table if it doesn't exist
CREATE TABLE IF NOT EXISTS users (
    user_id BIGSERIAL PRIMARY KEY,
    username VARCHAR(256) NOT NULL UNIQUE CHECK (username <> ''),
    pw_hash BYTEA NOT NULL,
    salt BYTEA NOT NULL,
    api_key TEXT NOT NULL UNIQUE
);


-- Ensure api_key column exists
ALTER TABLE users ADD COLUMN IF NOT EXISTS api_key TEXT NOT NULL UNIQUE;
