import asyncio
import os
import re
from sqlalchemy import text
from backend.database.database import engine, Base
from backend.database.models import *

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Tables are owned by the application role; grant read-only access to the dedicated admin role.
        admin_role = os.getenv("ADMIN_DB_USER", "lumira_admin_role")
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", admin_role):
            raise ValueError("ADMIN_DB_USER contains unsupported identifier characters")
        await conn.execute(text(f'GRANT SELECT ON ALL TABLES IN SCHEMA public TO "{admin_role}"'))
        rls_path = os.path.join(os.path.dirname(__file__), "..", "database", "setup_rls.sql")
        if os.path.exists(rls_path):
            with open(rls_path, "r", encoding="utf-8") as f:
                sql_content = f.read()
            # Strip comments
            sql_clean = re.sub(r'--.*', '', sql_content)
            for stmt in sql_clean.split(";"):
                stmt = stmt.strip()
                if stmt:
                    try:
                        await conn.execute(text(stmt))
                    except Exception as e:
                        # Policy might already exist or role not created yet
                        print(f"Notice during RLS setup ({stmt[:30]}...): {e}")
    print("Tables and RLS setup completed successfully.")

if __name__ == "__main__":
    asyncio.run(main())
