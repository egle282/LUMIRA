import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.database.models import Base, User, Tenant
from backend.core.config import settings
import asyncio
from sqlalchemy import text

import os
from dotenv import dotenv_values

_env = dotenv_values(".env")
_db_user = _env.get("DB_USER", "lumira")
_db_pass = _env.get("DB_PASSWORD", "")
_db_name = _env.get("DB_NAME", "lumira_db")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL") or f"postgresql+asyncpg://{_db_user}:{_db_pass}@127.0.0.1:5433/{_db_name}"

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    async with engine.begin() as conn:
        import re
        with open("backend/database/setup_rls.sql") as f:
            sql = f.read()
        sql = re.sub(r'--.*', '', sql)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        for statement in sql.split(";"):
            stmt = statement.strip()
            if stmt:
                await conn.execute(text(stmt))
        await conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'lumira_app') THEN
                    CREATE ROLE lumira_app NOLOGIN;
                END IF;
                IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'lumira_admin_role') THEN
                    CREATE ROLE lumira_admin_role WITH LOGIN PASSWORD 'admin_pass';
                END IF;
                -- Ensure lumira does not bypass RLS if running as superuser in CI container
                IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'lumira' AND (rolsuper = true OR rolbypassrls = true)) THEN
                    ALTER ROLE lumira NOSUPERUSER CREATEROLE NOBYPASSRLS;
                END IF;
            END
            $$;
        """))
        await conn.execute(text("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO lumira_app;"))
        await conn.execute(text("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO lumira_app;"))
        await conn.execute(text("GRANT lumira_app TO lumira;"))
        await conn.execute(text("GRANT CONNECT ON DATABASE lumira_db TO lumira_admin_role;"))
        await conn.execute(text("GRANT USAGE ON SCHEMA public TO lumira_admin_role;"))
        await conn.execute(text("GRANT SELECT ON ALL TABLES IN SCHEMA public TO lumira_admin_role;"))

    yield
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session(setup_db):
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with AsyncSessionLocal() as session:
        await session.execute(text("SET ROLE lumira_app;"))
        yield session
        await session.rollback()
    await engine.dispose()
