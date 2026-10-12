-- ===================================================================
-- AI STORYTELLING PLATFORM: POSTGRESQL INITIALIZATION SCRIPT
-- ===================================================================

-- 1. Create Dedicated Application User
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'storytelling_app') THEN

      CREATE ROLE storytelling_app WITH LOGIN PASSWORD 'storytelling_pass_2026';
   ELSE
      ALTER ROLE storytelling_app WITH PASSWORD 'storytelling_pass_2026';
   END IF;
END
$do$;

-- 2. Create Application Database
SELECT 'CREATE DATABASE storytelling_db OWNER storytelling_app'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'storytelling_db')\gexec

-- 3. Grant Permissions
GRANT ALL PRIVILEGES ON DATABASE storytelling_db TO storytelling_app;
ALTER DATABASE storytelling_db OWNER TO storytelling_app;

-- 4. Ensure Public Schema Privileges on storytelling_db (PostgreSQL 15+)
\c storytelling_db
GRANT ALL ON SCHEMA public TO storytelling_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO storytelling_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO storytelling_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO storytelling_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO storytelling_app;

