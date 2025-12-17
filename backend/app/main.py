from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import (
    auth_router,
    workers_router,
    properties_router,
    time_records_router,
    reports_router
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Internal Time & Cost Tracking System for DC Landscaping",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(workers_router, prefix="/api")
app.include_router(properties_router, prefix="/api")
app.include_router(time_records_router, prefix="/api")
app.include_router(reports_router, prefix="/api")

