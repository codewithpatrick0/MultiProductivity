from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

class BaseResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    name: str = Field(min_length=3, max_length=20, pattern=r"^[A-Za-záéíóúÁÉÍÓÚñÑ ]+$")
    username: str = Field(min_length=5, max_length=20)
    password: str = Field(min_length=8, max_length=24)

class UserResponse(BaseResponseSchema):
    name: str
    username: str
    active: bool

class TokenResponse(BaseResponseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(from_attributes=True)

class TaskCreate(BaseModel):
    title: str = Field(max_length=100)
    info: str | None

class TaskEdit(TaskCreate):
    status: Literal['pending', 'in progress', 'completed']
    
class TaskResponse(BaseResponseSchema):
    id: int
    id_user: int
    title: str 
    info: str | None 
    status: str = "pending"
