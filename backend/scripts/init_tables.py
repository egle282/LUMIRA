import asyncio
import os
import re

from sqlalchemy import text

from backend.database.database import engine, Base
from backend.database.models import *  # noqa: F403 - registers all ORM models


def _validated_role(name: str, env_name: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        raise ValueError(f"{env_name} contains unsupported identifier characters")
    return name


async def main() -> None:
    admin_role = _validated_role(
        os.getenv("ADMIN_DB_USER", "lumira_admin_role"), "ADMIN_DB_USER"
    )
    app_role = _validated_role(os.getenv("APP_DB_USER", "lumira_app"), "APP_DB_USER")

    rls_path = os.path.join(
        os.path.dirname(__file__), "..", "database", "setup_rls.sql"
    )
    with open(rls_path, "r", encoding="utf-8") as file:
        sql_content = file.read()
    sql_content = sql_content.replace("lumira_admin_role", admin_role)
    sql_clean = re.sub(r"--.*", "", sql_content)
    statements = [stmt.strip() for stmt in sql_clean.split(";") if stmt.strip()]

    async with engine.begin() as conn:
        # This one-shot init service connects as the database bootstrap role.
        # The runtime app role never owns tables and cannot alter RLS policies.
        await conn.run_sync(Base.metadata.create_all)
        # Repair databases initialized by older versions where the runtime role
        # owned the tables. Ownership would let it bypass FORCE RLS protections.
        await conn.execute(text("""
            DO $$
            DECLARE obj record;
            BEGIN
              FOR obj IN
                SELECT schemaname, tablename
                FROM pg_tables
                WHERE schemaname = 'public'
              LOOP
                EXECUTE format(
                  'ALTER TABLE %I.%I OWNER TO %I',
                  obj.schemaname, obj.tablename, current_user
                );
              END LOOP;
              FOR obj IN
                SELECT sequence_schema, sequence_name
                FROM information_schema.sequences
                WHERE sequence_schema = 'public'
              LOOP
                EXECUTE format(
                  'ALTER SEQUENCE %I.%I OWNER TO %I',
                  obj.sequence_schema, obj.sequence_name, current_user
                );
              END LOOP;
            END $;
        """))
        await conn.execute(text(f'REVOKE CREATE ON SCHEMA public FROM "{app_role}"'))
        await conn.execute(text(
            f'GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "{app_role}"'
        ))
        await conn.execute(text(
            f'GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO "{app_role}"'
        ))
        await conn.execute(text(
            f'GRANT SELECT ON ALL TABLES IN SCHEMA public TO "{admin_role}"'
        ))
        for statement in statements:
            await conn.execute(text(statement))

    print("Tables, runtime grants, and RLS policies initialized successfully.")


if __name__ == "__main__":
    asyncio.run(main())
