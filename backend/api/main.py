from fastapi import FastAPI
from core.config import settings
from core.logger import logger, setup_logging

app = FastAPI(title=settings.PROJECT_NAME)

@app.on_event("startup")
async def startup_event():
    setup_logging(settings.LOG_LEVEL)
    logger.info("Application starting up", project=settings.PROJECT_NAME)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}

@app.get("/api/ready")
async def readiness_check():
    # TODO: Add DB ping here
    return {"status": "ready"}
