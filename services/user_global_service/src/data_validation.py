from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# --- Enums ---
class EffectEnum(str, Enum):
    ALLOW = 'ALLOW'
    DENY = 'DENY'

# ==========================================
# User Validation Schemas
# ==========================================
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=255)
    status: Optional[int] = Field(1, description="1 for active, 0 for inactive")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    created_by: Optional[str] = None

class UserResponse(UserBase):
    user_id: int
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# ==========================================
# Role Validation Schemas
# ==========================================
class RoleBase(BaseModel):
    role_name: Optional[str] = Field(None, max_length=100)
    role_code: str = Field(..., max_length=50)
    description: Optional[str] = None
    status: Optional[int] = 1

class RoleCreate(RoleBase):
    created_by: Optional[str] = None

class RoleResponse(RoleBase):
    role_id: int
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# ==========================================
# Permission Validation Schemas
# ==========================================
class PermissionBase(BaseModel):
    permission_name: Optional[str] = Field(None, max_length=100)
    permission_code: str = Field(..., max_length=100)
    module: Optional[str] = Field(None, max_length=50)
    action: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    status: Optional[int] = 1

class PermissionCreate(PermissionBase):
    created_by: Optional[str] = None

class PermissionResponse(PermissionBase):
    permission_id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# ==========================================
# Attribute Validation Schemas (User & Resource)
# ==========================================
class UserAttributeBase(BaseModel):
    attribute_name: str = Field(..., max_length=100)
    attribute_value: str = Field(..., max_length=255)

class UserAttributeCreate(UserAttributeBase):
    user_id: int

class UserAttributeResponse(UserAttributeBase):
    user_attribute_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)

class ResourceAttributeBase(BaseModel):
    resource_type: str = Field(..., max_length=100)
    resource_id: str = Field(..., max_length=100)
    attribute_name: str = Field(..., max_length=100)
    attribute_value: str = Field(..., max_length=255)

class ResourceAttributeResponse(ResourceAttributeBase):
    resource_attribute_id: int

    model_config = ConfigDict(from_attributes=True)

# ==========================================
# Mapping/Junction Tables (UserRole & RolePermission)
# ==========================================
class UserRoleAssign(BaseModel):
    user_id: int
    role_id: int
    assigned_by: Optional[str] = None
    status: Optional[int] = 1

class RolePermissionAssign(BaseModel):
    role_id: int
    permission_id: int
    assigned_by: Optional[str] = None
    status: Optional[int] = 1

# ==========================================
# ABAC Policy Validation Schemas
# ==========================================
class AbacPolicyBase(BaseModel):
    policy_name: Optional[str] = Field(None, max_length=150)
    policy_code: str = Field(..., max_length=100)
    resource_type: Optional[str] = Field(None, max_length=100)
    action: Optional[str] = Field(None, max_length=100)
    effect: EffectEnum
    policy_definition: Optional[Dict[str, Any]] = None
    priority: Optional[int] = 1
    status: Optional[int] = 1

class AbacPolicyCreate(AbacPolicyBase):
    created_by: Optional[str] = None

class AbacPolicyResponse(AbacPolicyBase):
    policy_id: int
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)