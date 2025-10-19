from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional


class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone_number: Optional[str] = None

# CRUD Operation Schemas
class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: UUID

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None

class UserDelete(UserBase):
    id: UUID

    class Config:
        from_attributes = True