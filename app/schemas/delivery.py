from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime


class DeliveryCreate(BaseModel):
    material_id: int
    quantity: float
    delivered_at: datetime | None = None
    supplier: str | None = None
    comment: str | None = None

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("quantity must be positive")
        return v


class DeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    material_id: int
    quantity: float
    delivered_at: datetime
    supplier: str | None
    comment: str | None
