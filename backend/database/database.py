from fastapi import HTTPException
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from backend.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=(settings.ENVIRONMENT == "development"),
    future=True,
)

# Create session maker
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

admin_engine = None
AdminAsyncSessionLocal = None

if settings.ADMIN_DATABASE_URL:
    admin_engine = create_async_engine(
        settings.ADMIN_DATABASE_URL,
        echo=(settings.ENVIRONMENT == "development"),
        future=True,
    )
    AdminAsyncSessionLocal = async_sessionmaker(
        bind=admin_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def get_admin_db():
    if not AdminAsyncSessionLocal:
        raise HTTPException(status_code=503, detail="Admin database connection not configured")
    async with AdminAsyncSessionLocal() as session:
        yield session
