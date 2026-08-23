from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from models.event_task import TaskStatus, TaskPriority


# Các field cơ bản của một task.
class EventTaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None


# Schema request khi tạo task; assignee là tùy chọn.
class EventTaskCreate(EventTaskBase):
    assignee_id: Optional[int] = None


# Schema PATCH task; chỉ các field được gửi mới được cập nhật.
class EventTaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None


# Schema response cho task.
class EventTaskResponse(EventTaskBase):
    id: int
    event_id: int
    assignee_id: Optional[int] = None
    status: TaskStatus
    created_at: datetime

    # Cho phép serialize từ SQLAlchemy ORM object.
    model_config = ConfigDict(from_attributes=True)
