from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.admin.router import admin_router
from backend.memory.router import router as memory_router
from backend.astrology.router import router as astrology_router
from backend.astrology.muhurta_api import router as muhurta_router
from backend.briefing.router import router as briefing_router
from backend.api.auth import router as auth_router, get_password_hash
from backend.api.chat import router as chat_router
from backend.api.chart import router as chart_router
from backend.api.profile import router as profile_router
from backend.api.billing import router as billing_router

from backend.core.config import settings
from backend.database.database import AsyncSessionLocal, AdminAsyncSessionLocal
from backend.database.models import User, Tenant
from sqlalchemy.future import select
from sqlalchemy import text
from fastapi import Depends
import time
import json
import uuid
import logging
from fastapi.responses import JSONResponse
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("lumira.api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
        # Reuse the RLS-aware bootstrap path so the first administrator is
        # created with tenant context established before protected inserts.
        from backend.scripts.create_admin import create_admin

        await create_admin(settings.ADMIN_EMAIL, settings.ADMIN_PASSWORD)
    yield

app = FastAPI(title="LUMIRA API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(admin_router)
app.include_router(memory_router, prefix="/api")
app.include_router(astrology_router, prefix="/api")
app.include_router(muhurta_router, prefix="/api")
app.include_router(briefing_router, prefix="/api")
app.include_router(chart_router, prefix="/api")
app.include_router(profile_router, prefix="/api")
app.include_router(billing_router, prefix="/api")

class TelemetryMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        correlation_id = request.headers.get("X-Correlation-ID")
        # Validate correlation_id format or length to prevent log forging
        if not correlation_id or len(correlation_id) > 50 or not correlation_id.isascii():
            correlation_id = str(uuid.uuid4())
        
        request.state.correlation_id = correlation_id
        
        response = await call_next(request)
        process_time = time.time() - start_time
        
        log_data = {
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": round(process_time * 1000, 2)
        }
        logger.info(json.dumps(log_data))
        
        response.headers["X-Correlation-ID"] = correlation_id
        return response

app.add_middleware(TelemetryMiddleware)

from backend.api.deps import get_db

@app.get("/api/health")
async def health_check(db = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Health check DB failure: {e}")
        return JSONResponse(status_code=503, content={"status": "error", "message": "Service unavailable"})

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
    logger.error(f"Unhandled exception [ID: {correlation_id}]: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please contact support.",
            "correlation_id": correlation_id
        }
    )
