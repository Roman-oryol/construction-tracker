from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime


class ConsumptionCreate(BaseModel):
    material_id: int
    quantity: float
    consumed_at: datetime | None = None
    brigade: str | None = None
    comment: str | None = None

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("quantity must be positive")
        return v


class ConsumptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    material_id: int
    quantity: float
    consumed_at: datetime
    brigade: str | None
    comment: str | None
