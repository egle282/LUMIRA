import asyncio
import os
import re

from sqlalchemy import text

from backend.database.database import engine, Base
from backend.database.models import *  # noqa: F403 - registers all ORM models


async def main() -> None:
    admin_role = os.getenv("ADMIN_DB_USER", "lumira_admin_role")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", admin_role):
        raise ValueError("ADMIN_DB_USER contains unsupported identifier characters")

    rls_path = os.path.join(
        os.path.dirname(__file__), "..", "database", "setup_rls.sql"
    )
    with open(rls_path, "r", encoding="utf-8") as file:
        sql_content = file.read()
    sql_clean = re.sub(r"--.*", "", sql_content)
    statements = [stmt.strip() for stmt in sql_clean.split(";") if stmt.strip()]

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            text(f'GRANT SELECT ON ALL TABLES IN SCHEMA public TO "{admin_role}"')
        )
        # Do not silently continue: a database without working RLS is unsafe.
        for statement in statements:
            await conn.execute(text(statement))

    print("Tables and RLS policies initialized successfully.")


if __name__ == "__main__":
    asyncio.run(main())
