#!/bin/bash
set -euo pipefail

APP_DB_USER=${APP_DB_USER:-lumira_app}
APP_DB_PASSWORD=${APP_DB_PASSWORD:?APP_DB_PASSWORD must be set}
ADMIN_DB_USER=${ADMIN_DB_USER:-lumira_admin_role}
ADMIN_DB_PASSWORD=${ADMIN_DB_PASSWORD:?ADMIN_DB_PASSWORD must be set}

for role in "$APP_DB_USER" "$ADMIN_DB_USER"; do
  if [[ ! "$role" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
    echo "Invalid PostgreSQL role identifier: $role" >&2
    exit 1
  fi
done
if [[ "$APP_DB_USER" == "$ADMIN_DB_USER" ]]; then
  echo "APP_DB_USER and ADMIN_DB_USER must be different roles" >&2
  exit 1
fi

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  --set=app_role="$APP_DB_USER" --set=app_password="$APP_DB_PASSWORD" \
  --set=admin_role="$ADMIN_DB_USER" --set=admin_password="$ADMIN_DB_PASSWORD" \
  --set=db_name="$POSTGRES_DB" <<'EOSQL'
SELECT format(
  'CREATE ROLE %I LOGIN PASSWORD %L NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS',
  :'app_role', :'app_password'
)
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = :'app_role')
\gexec
SELECT format(
  'ALTER ROLE %I WITH LOGIN PASSWORD %L NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS',
  :'app_role', :'app_password'
)
\gexec

SELECT format(
  'CREATE ROLE %I LOGIN PASSWORD %L NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS',
  :'admin_role', :'admin_password'
)
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = :'admin_role')
\gexec
SELECT format(
  'ALTER ROLE %I WITH LOGIN PASSWORD %L NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS',
  :'admin_role', :'admin_password'
)
\gexec

GRANT CONNECT ON DATABASE :"db_name" TO :"app_role";
GRANT CONNECT ON DATABASE :"db_name" TO :"admin_role";
GRANT USAGE ON SCHEMA public TO :"app_role";
GRANT USAGE ON SCHEMA public TO :"admin_role";
GRANT SELECT ON ALL TABLES IN SCHEMA public TO :"admin_role";
ALTER DEFAULT PRIVILEGES FOR ROLE :"POSTGRES_USER" IN SCHEMA public GRANT SELECT ON TABLES TO :"admin_role";
EOSQL
