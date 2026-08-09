from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class PaymentMode(str, Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"


class LineItem(BaseModel):
    drug_name: str = Field(min_length=1)
    qty: int = Field(gt=0)
    unit_price_paise: int = Field(ge=0)


class BillingRecord(BaseModel):
    clinic_id: str = Field(min_length=1)
    visit_id: str = Field(min_length=1)
    timestamp: datetime
    doctor_id: str = Field(min_length=1)

    line_items: list[LineItem] = Field(min_length=1)

    payment_mode: PaymentMode
    amount_paid_paise: int
    discount_paise: int = Field(ge=0)

    is_refund: bool