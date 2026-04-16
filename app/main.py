from fastapi import FastAPI
from app.core.config import settings
from app.core.database import init_db
from app.api.routes import router
from app.models import request_log

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

app.include_router(router, prefix="/api/v1")

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }