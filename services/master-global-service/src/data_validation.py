
import re
from datetime import date, datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class VendorBase(BaseModel):
    vendor_name: str = Field(
        min_length=1,
        max_length=100,
    )

    phone_number: str | None = Field(
        default=None,
        max_length=20,
    )

    gst_number: str | None = Field(
        default=None,
        max_length=15,
    )

    status: str | None = Field(
        default="ACTIVE",
        max_length=20,
    )

    created_date: date | None = None

    created_by: str | None = Field(
        default=None,
        max_length=50,
    )

    phone_number1: str | None = Field(
        default=None,
        max_length=20,
    )

    pan_number: str | None = Field(
        default=None,
        max_length=15,
    )

    address: str | None = Field(
        default=None,
        max_length=255,
    )

    bank_name: str | None = Field(
        default=None,
        max_length=100,
    )

    branch_name: str | None = Field(
        default=None,
        max_length=150,
    )

    account_no: str | None = Field(
        default=None,
        max_length=50,
    )

    ifsc_code: str | None = Field(
        default=None,
        max_length=20,
    )

    msme_no: str | None = Field(
        default=None,
        max_length=50,
    )

    updated_by: str | None = Field(
        default=None,
        max_length=100,
    )

    updated_date: datetime | None = None

    @field_validator("vendor_name")
    @classmethod
    def validate_vendor_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Vendor name cannot be empty")

        return value

    @field_validator("phone_number", "phone_number1")
    @classmethod
    def validate_phone_number(
        cls, value: str | None
    ) -> str | None:
        if value is None or not value.strip():
            return None

        value = value.strip()

        # Allow digits, an optional leading +, spaces,
        # and common phone-number separators.
        if not re.fullmatch(r"\+?[0-9\s()-]+", value):
            raise ValueError("Invalid phone number format")

        digits = re.sub(r"\D", "", value)

        if not 7 <= len(digits) <= 15:
            raise ValueError(
                "Phone number must contain 7 to 15 digits"
            )

        return value

    @field_validator("gst_number")
    @classmethod
    def validate_gst_number(
        cls, value: str | None
    ) -> str | None:
        if value is None or not value.strip():
            return None

        value = value.strip().upper()

        # Standard Indian GSTIN structure.
        pattern = (
            r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]"
            r"[1-9A-Z]Z[0-9A-Z]$"
        )

        if not re.fullmatch(pattern, value):
            raise ValueError("Invalid GST number format")

        return value

    @field_validator("pan_number")
    @classmethod
    def validate_pan_number(
        cls, value: str | None
    ) -> str | None:
        if value is None or not value.strip():
            return None

        value = value.strip().upper()

        if not re.fullmatch(
            r"[A-Z]{5}[0-9]{4}[A-Z]", value
        ):
            raise ValueError("Invalid PAN number format")

        return value

    @field_validator("ifsc_code")
    @classmethod
    def validate_ifsc_code(
        cls, value: str | None
    ) -> str | None:
        if value is None or not value.strip():
            return None

        value = value.strip().upper()

        if not re.fullmatch(
            r"[A-Z]{4}0[A-Z0-9]{6}", value
        ):
            raise ValueError("Invalid IFSC code format")

        return value

    @field_validator("status")
    @classmethod
    def validate_status(
        cls, value: str | None
    ) -> str | None:
        if value is None:
            return value

        value = value.strip().upper()

        allowed_statuses = {
            "ACTIVE",
            "INACTIVE",
            "BLOCKED",
        }

        if value not in allowed_statuses:
            raise ValueError(
                "Status must be ACTIVE, INACTIVE, or BLOCKED"
            )

        return value


class VendorCreate(VendorBase):
    vendor_code: str = Field(
        min_length=1,
        max_length=15,
    )

    @field_validator("vendor_code")
    @classmethod
    def validate_vendor_code(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Vendor code cannot be empty")

        return value


class VendorUpdate(BaseModel):
    vendor_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    phone_number: str | None = Field(
        default=None,
        max_length=20,
    )
    gst_number: str | None = Field(
        default=None,
        max_length=15,
    )
    status: str | None = Field(
        default=None,
        max_length=20,
    )
    phone_number1: str | None = Field(
        default=None,
        max_length=20,
    )
    pan_number: str | None = Field(
        default=None,
        max_length=15,
    )
    address: str | None = Field(
        default=None,
        max_length=255,
    )
    bank_name: str | None = Field(
        default=None,
        max_length=100,
    )
    branch_name: str | None = Field(
        default=None,
        max_length=150,
    )
    account_no: str | None = Field(
        default=None,
        max_length=50,
    )
    ifsc_code: str | None = Field(
        default=None,
        max_length=20,
    )
    msme_no: str | None = Field(
        default=None,
        max_length=50,
    )
    updated_by: str | None = Field(
        default=None,
        max_length=100,
    )

    @field_validator("vendor_name")
    @classmethod
    def validate_updated_vendor_name(
        cls, value: str | None
    ) -> str | None:
        if value is None:
            return value

        value = value.strip()

        if not value:
            raise ValueError("Vendor name cannot be empty")

        return value

    @field_validator("phone_number", "phone_number1")
    @classmethod
    def validate_updated_phone(
        cls, value: str | None
    ) -> str | None:
        return VendorBase.validate_phone_number(value)

    @field_validator("gst_number")
    @classmethod
    def validate_updated_gst(
        cls, value: str | None
    ) -> str | None:
        return VendorBase.validate_gst_number(value)

    @field_validator("pan_number")
    @classmethod
    def validate_updated_pan(
        cls, value: str | None
    ) -> str | None:
        return VendorBase.validate_pan_number(value)

    @field_validator("ifsc_code")
    @classmethod
    def validate_updated_ifsc(
        cls, value: str | None
    ) -> str | None:
        return VendorBase.validate_ifsc_code(value)

    @field_validator("status")
    @classmethod
    def validate_updated_status(
        cls, value: str | None
    ) -> str | None:
        return VendorBase.validate_status(value)


class VendorResponse(VendorBase):
    model_config = ConfigDict(from_attributes=True)

    vendor_code: str
