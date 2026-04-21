from pydantic import BaseModel, ConfigDict


class MaterialBase(BaseModel):
    name: str
    unit: str
    low_stock_threshold: float = 0
    description: str | None = None


class MaterialCreate(MaterialBase):
    project_id: int


class MaterialUpdate(BaseModel):
    name: str | None = None
    unit: str | None = None
    low_stock_threshold: float | None = None
    description: str | None = None


class MaterialResponse(MaterialBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    current_stock: float = 0
