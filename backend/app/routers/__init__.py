from app.routers.auth import router as auth_router
from app.routers.workers import router as workers_router
from app.routers.properties import router as properties_router
from app.routers.time_records import router as time_records_router
from app.routers.reports import router as reports_router

__all__ = [
    "auth_router",
    "workers_router", 
    "properties_router",
    "time_records_router",
    "reports_router",
]
