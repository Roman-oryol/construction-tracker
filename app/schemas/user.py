from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str | None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
