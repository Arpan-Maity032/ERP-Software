import os
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    create_engine, String, Integer, BigInteger, DateTime, Text, JSON, SmallInteger, ForeignKey, Enum
)

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship
from sqlalchemy.engine import URL

DB_NAME = os.environ.get("DB_NAME", "default_db")


engine = create_engine(
    URL.create(
        "mysql+pymysql",
        username=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD",""),
        host=os.getenv("DB_HOST", "mysql"),
        port=3306,
        database=DB_NAME,
    ),
    pool_pre_ping=True,
    pool_recycle=1800,
)
sessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass

class UserMaster(Base):
    __tablename__ = "user_master"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    modified_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    modified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    user_roles: Mapped[list["UserRole"]] = relationship("UserRole", back_populates="user")
    attributes: Mapped[list["UserAttribute"]] = relationship("UserAttribute")

class UserAttribute(Base):
    __tablename__ = "user_attribute"

    user_attribute_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_master.user_id"))
    attribute_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    attribute_value: Mapped[str | None] = mapped_column(String(255), nullable=True)


class RoleMaster(Base):
    __tablename__ = "role_master"

    role_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    role_code: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    modified_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    modified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class UserRole(Base):
    __tablename__ = "user_role"

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_master.user_id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("role_master.role_id"), primary_key=True)
    assigned_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    user: Mapped["UserMaster"] = relationship("UserMaster", back_populates="user_roles")
    role: Mapped["RoleMaster"] = relationship("RoleMaster")


class PermissionMaster(Base):
    __tablename__ = "permission_master"

    permission_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    permission_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    permission_code: Mapped[str] = mapped_column(String(100), unique=True)
    module: Mapped[str | None] = mapped_column(String(50), nullable=True)
    action: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    modified_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    modified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class RolePermission(Base):
    __tablename__ = "role_permission"

    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("role_master.role_id"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey("permission_master.permission_id"), primary_key=True)
    assigned_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)


class ResourceAttribute(Base):
    __tablename__ = "resource_attribute"

    resource_attribute_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    resource_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    attribute_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    attribute_value: Mapped[str | None] = mapped_column(String(255), nullable=True)


class AbacPolicy(Base):
    __tablename__ = "abac_policy"

    policy_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    policy_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    policy_code: Mapped[str] = mapped_column(String(100), unique=True)
    resource_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    action: Mapped[str | None] = mapped_column(String(100), nullable=True)
    effect: Mapped[str | None] = mapped_column(Enum('ALLOW', 'DENY', name="effect_enum"), nullable=True)
    policy_definition: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    priority: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    modified_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    modified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)