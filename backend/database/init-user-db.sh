#!/bin/bash
set -e

# Create a dedicated, non-superuser role for the application to connect with.
# This ensures that RLS (Row Level Security) is strictly enforced and cannot be bypassed.

APP_DB_USER=${APP_DB_USER:-lumira_app}
APP_DB_PASSWORD=${APP_DB_PASSWORD:-lumira_app_password}
ADMIN_DB_USER=${ADMIN_DB_USER:-lumira_admin_role}
ADMIN_DB_PASSWORD=${ADMIN_DB_PASSWORD:-lumira_admin_password}

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$APP_DB_USER') THEN
            CREATE ROLE $APP_DB_USER WITH LOGIN PASSWORD '$APP_DB_PASSWORD';
        ELSE
            ALTER ROLE $APP_DB_USER WITH PASSWORD '$APP_DB_PASSWORD';
        END IF;

        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$ADMIN_DB_USER') THEN
            CREATE ROLE $ADMIN_DB_USER WITH LOGIN PASSWORD '$ADMIN_DB_PASSWORD';
        ELSE
            ALTER ROLE $ADMIN_DB_USER WITH PASSWORD '$ADMIN_DB_PASSWORD';
        END IF;
    END
    \$\$;

    -- Grants for application role (RLS strictly enforced)
    GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $APP_DB_USER;
    GRANT ALL ON SCHEMA public TO $APP_DB_USER;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $APP_DB_USER;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $APP_DB_USER;

    -- Grants for admin role (Read-only for cross-tenant reporting, NO SUPERUSER, NO BYPASSRLS)
    GRANT CONNECT ON DATABASE $POSTGRES_DB TO $ADMIN_DB_USER;
    GRANT USAGE ON SCHEMA public TO $ADMIN_DB_USER;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO $ADMIN_DB_USER;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO $ADMIN_DB_USER;
EOSQL
