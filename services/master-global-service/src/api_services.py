
import os
from datetime import datetime, timezone

import jwt
from fastapi import (
    APIRouter,
    Depends,
    Header,
    HTTPException,
    Query,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from database_schema import SessionLocal, Vendor
from data_validation import (
    VendorCreate,
    VendorUpdate,
    VendorResponse,
)


SERVICE = os.getenv("SERVICE_NAME", "master-global")

JWT_SECRET = os.environ.get("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET environment variable is required")

ALGORITHM = "HS256"

router = APIRouter()


# DATABASE SESSION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# AUTHENTICATION
def current_user(
    authorization: str | None = Header(default=None),
) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Bearer access token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ", 1)[1]

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role", "user")

        if not user_id or not email:
            raise HTTPException(
                status_code=401,
                detail="Invalid access token payload",
            )

        return {
            "id": str(user_id),
            "email": email,
            "role": role,
        }

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_admin(
    user: dict = Depends(current_user),
) -> dict:
    if user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin role required",
        )

    return user


# VENDOR SERVICE


# CREATE VENDOR
@router.post(
    "/api/v1/master",
    response_model=VendorResponse,
    status_code=201,
)
def create_vendor(
    data: VendorCreate,
    user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    existing = db.get(Vendor, data.vendor_code)

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Vendor code already exists",
        )

    vendor_data = data.model_dump()

    # Audit fields should come from the authenticated identity.
    vendor_data["created_by"] = user["email"]
    vendor_data["created_date"] = datetime.now(
        timezone.utc
    ).date()

    vendor = Vendor(**vendor_data)

    try:
        db.add(vendor)
        db.commit()
        db.refresh(vendor)
        return vendor

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Vendor code or another unique value already exists",
        )

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while creating vendor",
        )


@router.get(
    "/api/v1/master",
    response_model=list[VendorResponse],
)
def list_vendors(
    user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
    q: str | None = Query(default=None, max_length=100),
    status: str | None = Query(default=None, max_length=20),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    stmt = select(Vendor)

    if q:
        search = q.strip()
        stmt = stmt.where(
            Vendor.vendor_code.ilike(f"%{search}%")
            | Vendor.vendor_name.ilike(f"%{search}%")
        )

    if status:
        stmt = stmt.where(
            Vendor.status == status.strip().upper()
        )

    stmt = (
        stmt.order_by(Vendor.vendor_code)
        .limit(limit)
        .offset(offset)
    )

    return db.scalars(stmt).all()


# GET VENDOR BY CODE
@router.get(
    "/api/v1/master/{vendor_code}",
    response_model=VendorResponse,
)
def get_vendor(
    vendor_code: str,
    user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    vendor = db.get(Vendor, vendor_code)

    if not vendor:
        raise HTTPException(
            status_code=404,
            detail="Vendor not found",
        )

    return vendor


# UPDATE VENDOR
@router.patch(
    "/api/v1/master/{vendor_code}",
    response_model=VendorResponse,
)
def update_vendor(
    vendor_code: str,
    data: VendorUpdate,
    user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    vendor = db.get(Vendor, vendor_code)

    if not vendor:
        raise HTTPException(
            status_code=404,
            detail="Vendor not found",
        )

    updates = data.model_dump(exclude_unset=True)

    # Do not allow a client to clear fields that must be populated.
    if "vendor_name" in updates and updates["vendor_name"] is None:
        raise HTTPException(
            status_code=422,
            detail="Vendor name cannot be null",
        )

    for field, value in updates.items():
        setattr(vendor, field, value)

    vendor.updated_by = user["email"]
    vendor.updated_date = datetime.now(timezone.utc).replace(
        tzinfo=None
    )

    try:
        db.commit()
        db.refresh(vendor)
        return vendor

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Vendor update conflicts with a database constraint",
        )

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while updating vendor",
        )


# DEACTIVATE VENDOR
@router.delete(
    "/api/v1/master/{vendor_code}",
)
def deactivate_vendor(
    vendor_code: str,
    user: dict = Depends(require_admin),
    db: Session = Depends(get_db),
):
    vendor = db.get(Vendor, vendor_code)

    if not vendor:
        raise HTTPException(
            status_code=404,
            detail="Vendor not found",
        )

    vendor.status = "INACTIVE"
    vendor.updated_by = user["email"]
    vendor.updated_date = datetime.now(timezone.utc).replace(
        tzinfo=None
    )

    try:
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error while deactivating vendor",
        )

    return {
        "message": "Vendor deactivated successfully",
        "vendor_code": vendor.vendor_code,
        "status": vendor.status,
    }
