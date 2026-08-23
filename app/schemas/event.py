from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


# Các field dùng chung khi tạo/đọc Event.
class EventBase(BaseModel):
    # Field giúp Pydantic tự kiểm tra độ dài name ngay từ request.
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# Schema dùng cho request POST tạo Event.
class EventCreate(EventBase):
    pass


# Schema dùng cho PATCH; tất cả field đều optional để hỗ trợ partial update.
class EventUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# Schema response trả dữ liệu Event ra API.
class EventResponse(EventBase):
    id: int
    owner_id: int
    created_at: datetime
    is_deleted: bool

    # Cho phép Pydantic đọc dữ liệu trực tiếp từ SQLAlchemy model.
    model_config = ConfigDict(from_attributes=True)
