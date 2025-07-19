import logging

from fastapi import FastAPI, Depends
from fastapi.openapi.utils import get_openapi

from app.config import config
from app.db.models.models import Base
from app.db.session import engine
from app.routers.user_auth_router import user_auth_router
from app.routers.location import location_router
from app.routers.appointment_router import appointment_router
from app.routers.admin_router import admin_router
from app.routers.report_router import report_router
from app.routers.health_router import health_router

from app.dependencies.auth import get_current_user


def create_tables():         
	Base.metadata.create_all(bind=engine)
      
def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(title=config.PROJECT_NAME, version=config.PROJECT_VERSION,routes=app.routes)
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    openapi_schema["security"] = [{"Bearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema
        

def start_application():
    app = FastAPI(title=config.PROJECT_NAME, version=config.PROJECT_VERSION,docs_url=f"{config.API_PREFIX}/api-docs",openapi_url=f"{config.API_PREFIX}/openapi.json")
    create_tables()
    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    app.include_router(user_auth_router)
    app.include_router(location_router)
    app.include_router(appointment_router)
    app.include_router(report_router)
    app.include_router(admin_router)
    app.include_router(health_router)
    # custom_openapi(app)
    return app




