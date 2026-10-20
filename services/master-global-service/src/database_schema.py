import os
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    create_engine, String, Integer, DateTime, Date, Text, Boolean, Numeric
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.engine import URL

DB_NAME = os.environ.get("DB_NAME", "default_db")

engine = create_engine(
    URL.create(
        "mysql+pymysql",
        username=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        host=os.getenv("DB_HOST", "mysql"),
        port=3306,
        database=DB_NAME,
    ),
    pool_pre_ping=True,
    pool_recycle=1800,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Vendor(Base):
    __tablename__ = "emc_vendor_master"

    vendor_code: Mapped[str] = mapped_column(
        String(15), primary_key=True
    )
    vendor_name: Mapped[str] = mapped_column(
        String(100)
    )
    phone_number: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )
    gst_number: Mapped[str | None] = mapped_column(
        String(15), nullable=True
    )
    status: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )
    created_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    created_by: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    phone_number1: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )
    pan_number: Mapped[str | None] = mapped_column(
        String(15), nullable=True
    )
    address: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    bank_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    branch_name: Mapped[str | None] = mapped_column(
        String(150), nullable=True
    )
    account_no: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    ifsc_code: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )
    msme_no: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    updated_by: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    updated_date: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
