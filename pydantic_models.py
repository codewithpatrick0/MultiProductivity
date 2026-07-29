from datetime import date, datetime
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

class TaskCreate(BaseModel):
    id_category: int | None = None
    id_parent_task: int | None = None
    title: str = Field(min_length=3, max_length=100)
    info: str | None = None
    priority: int | None = Field(None, ge=1, le=1000)
    due_date: date | None = None
    reminder_at: datetime | None = None

class TaskEdit(BaseModel):
    id_category: int | None = None
    id_parent_task: int | None = None
    title: str | None = Field(None, max_length=100)
    info: str | None = None
    status: Literal['pending', 'in progress', 'completed'] | None = None
    priority: int | None = Field(None, ge=1, le=1000)
    due_date: date | None = None
    reminder_at: datetime | None = None

class TaskResponse(BaseResponseSchema):
    id: int
    id_user: int
    id_category: int
    id_parent_task: int | None = None
    title: str
    info: str | None = None
    status: str = "pending"
    priority: int
    due_date: date | None = None
    reminder_at: datetime | None = None

class CategoryCreate(BaseModel):
    name: str = Field(max_length=30)
    color: str = Field(max_length=20)

class CategoryEdit(BaseModel):
    name: str | None = Field(None, max_length=30)
    color: str | None = Field(None, max_length=20)

class CategoryResponse(BaseResponseSchema):
    id: int
    id_user: int | None = None
    name: str
    color: str