from pydantic import BaseModel, Field, field_validator

class UserCreate(BaseModel):
    name: str = Field(min_length=5, max_length=20, pattern=r"^[A-Za-záéíóúÁÉÍÓÚñÑ ]+$")
    username: str = Field(min_length=5, max_length=20)
    password: str = Field(min_length=8, max_length=24)

class UserResponse(BaseModel):
    name: str
    username: str
    active: bool

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"