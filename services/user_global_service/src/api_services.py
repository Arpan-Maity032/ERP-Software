import os
from datetime import datetime, timezone
import jwt
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

# Corrected imports to match standard filenames
from database_schema import (
    SessionLocal, UserMaster, RoleMaster, PermissionMaster, 
    UserRole, RolePermission, AbacPolicy
)
from data_validation import (
    UserCreate, UserResponse, RoleCreate, RoleResponse,
    PermissionCreate, PermissionResponse, AbacPolicyCreate, AbacPolicyResponse,
    UserRoleAssign, RolePermissionAssign
)

SERVICE = os.getenv("SERVICE_NAME", "rbac-abac-service")
JWT_SECRET = os.environ.get("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET environment variable is required")

ALGORITHM = "HS256"
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Bearer access token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role", "user")

        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid access token payload")

        return {"id": str(user_id), "email": email, "role": role}
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401, detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_admin(user: dict = Depends(current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user

@router.post("/api/v1/users", response_model=UserResponse, status_code=201)
def create_user(data: UserCreate, user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    user_data = data.model_dump(exclude={"password"})
    user_data["password_hash"] = f"hashed_{data.password}" 
    user_data["created_by"] = user["email"]
    user_data["created_at"] = datetime.now(timezone.utc).replace(tzinfo=None)

    new_user = UserMaster(**user_data)
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="User email already exists")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while creating user")

@router.get("/api/v1/users", response_model=list[UserResponse])
def list_users(user: dict = Depends(require_admin), db: Session = Depends(get_db), limit: int = Query(20, ge=1), offset: int = Query(0, ge=0)):
    stmt = select(UserMaster).limit(limit).offset(offset)
    return db.scalars(stmt).all()

@router.post("/api/v1/roles", response_model=RoleResponse, status_code=201)
def create_role(data: RoleCreate, user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    role_data = data.model_dump()
    role_data["created_by"] = user["email"]
    role_data["created_at"] = datetime.now(timezone.utc).replace(tzinfo=None)

    new_role = RoleMaster(**role_data)
    try:
        db.add(new_role)
        db.commit()
        db.refresh(new_role)
        return new_role
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Role code already exists")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while creating role")

@router.get("/api/v1/roles", response_model=list[RoleResponse])
def list_roles(user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    stmt = select(RoleMaster)
    return db.scalars(stmt).all()

@router.post("/api/v1/permissions", response_model=PermissionResponse, status_code=201)
def create_permission(data: PermissionCreate, user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    perm_data = data.model_dump()
    perm_data["created_by"] = user["email"]
    perm_data["created_at"] = datetime.now(timezone.utc).replace(tzinfo=None)

    new_perm = PermissionMaster(**perm_data)
    try:
        db.add(new_perm)
        db.commit()
        db.refresh(new_perm)
        return new_perm
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Permission code already exists")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while creating permission")

@router.post("/api/v1/users/{user_id}/roles", status_code=201)
def assign_role_to_user(user_id: int, data: UserRoleAssign, admin: dict = Depends(require_admin), db: Session = Depends(get_db)):
    if user_id != data.user_id:
        raise HTTPException(status_code=400, detail="Path user_id does not match payload")
    
    assignment = UserRole(
        user_id=data.user_id,
        role_id=data.role_id,
        assigned_by=admin["email"],
        assigned_at=datetime.now(timezone.utc).replace(tzinfo=None),
        status=data.status
    )
    try:
        db.add(assignment)
        db.commit()
        return {"message": "Role assigned successfully"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="User already has this role or invalid IDs")

@router.post("/api/v1/policies", response_model=AbacPolicyResponse, status_code=201)
def create_policy(data: AbacPolicyCreate, user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    policy_data = data.model_dump()
    policy_data["created_by"] = user["email"]
    policy_data["created_at"] = datetime.now(timezone.utc).replace(tzinfo=None)

    new_policy = AbacPolicy(**policy_data)
    try:
        db.add(new_policy)
        db.commit()
        db.refresh(new_policy)
        return new_policy
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Policy code already exists")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while creating policy")

@router.get("/api/v1/policies", response_model=list[AbacPolicyResponse])
def list_policies(user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    stmt = select(AbacPolicy).order_by(AbacPolicy.priority.desc())
    return db.scalars(stmt).all()