-- Bootstrap script: creates the repairmatrix role and database.
-- Must be run against an existing database (e.g. the default $USER db),
-- because CREATE DATABASE cannot run inside the target database itself.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = 'repairmatrix') THEN
        CREATE ROLE repairmatrix LOGIN PASSWORD 'password123';
    END IF;
END
$$;

SELECT 'CREATE DATABASE repairmatrix OWNER repairmatrix'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'repairmatrix')\gexec

GRANT ALL PRIVILEGES ON DATABASE repairmatrix TO repairmatrix;
