from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class TaskBase(BaseModel):
    title: str
    status: int = 0
    due_date: Optional[datetime] = None

# CRUD Operation Schemas
class TaskCreate(TaskBase):
    user_id: UUID

class TaskRead(TaskBase):
    id: UUID
    user_id: UUID

    class Config:
        from_attributes = True

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[int] = None
    due_date: Optional[datetime] = None

class TaskDelete(TaskBase):
    id: UUID

    class Config:
        from_attributes = True