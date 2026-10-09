import asyncio
from backend.database.database import engine, Base
from backend.database.models import User, Memory

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created")

if __name__ == "__main__":
    asyncio.run(init_models())
