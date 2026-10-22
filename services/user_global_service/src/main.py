from fastapi import FastAPI, HTTPException

# Import configuration and models from the updated database schema
from database_schema_3 import (
    Base, 
    engine, 
    DB_NAME, 
    UserMaster, 
    UserAttribute, 
    RoleMaster, 
    UserRole, 
    PermissionMaster, 
    RolePermission, 
    ResourceAttribute, 
    AbacPolicy
)

# Import router and service configuration
from api_services import router, SERVICE

app = FastAPI(
    title=f"{SERVICE.title()} API",
    version="1.0.0"
)


@app.on_event("startup")
def startup():
    """
    Create only the database tables owned by this service.
    """
    owned_models = {
        "rbac-abac-service": [
            UserMaster,
            UserAttribute,
            RoleMaster,
            UserRole,
            PermissionMaster,
            RolePermission,
            ResourceAttribute,
            AbacPolicy
        ],
    }

    if SERVICE in owned_models:
        Base.metadata.create_all(
            bind=engine,
            tables=[
                model.__table__
                for model in owned_models[SERVICE]
            ]
        )


@app.get("/health")
def health():
    """
    Check whether the database connection is available.
    """
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")

        return {
            "status": "healthy",
            "service": SERVICE,
            "database": DB_NAME
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        )


@app.get("/")
def root():
    return {
        "service": SERVICE,
        "docs": "/docs",
        "health": "/health"
    }


app.include_router(router)