from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.admin.router import admin_router
from backend.memory.router import router as memory_router
from backend.astrology.router import router as astrology_router
from backend.briefing.router import router as briefing_router
from backend.api.auth import router as auth_router, get_password_hash
from backend.api.chat import router as chat_router
from backend.api.chart import router as chart_router
from backend.api.profile import router as profile_router
from backend.api.billing import router as billing_router

from backend.core.config import settings
from backend.database.database import AsyncSessionLocal
from backend.database.models import User, Tenant
from sqlalchemy.future import select

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
        async with AsyncSessionLocal() as session:
            stmt = select(User).where(User.email == settings.ADMIN_EMAIL)
            result = await session.execute(stmt)
            if not result.scalars().first():
                # create system tenant
                new_tenant = Tenant(name="System Admin")
                session.add(new_tenant)
                await session.commit()
                await session.refresh(new_tenant)
                
                # create admin user
                new_user = User(
                    tenant_id=new_tenant.id,
                    email=settings.ADMIN_EMAIL,
                    role="admin",
                    hashed_password=get_password_hash(settings.ADMIN_PASSWORD)
                )
                session.add(new_user)
                await session.commit()
                print(f"Created default admin user: {settings.ADMIN_EMAIL}")
    yield

app = FastAPI(title="LUMIRA API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(admin_router)
app.include_router(memory_router, prefix="/api")
app.include_router(astrology_router, prefix="/api")
app.include_router(briefing_router, prefix="/api")
app.include_router(chart_router, prefix="/api")
app.include_router(profile_router, prefix="/api")

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
