from datetime import datetime
from pydantic import BaseModel, ConfigDict
from models.event_staff import EventStaffRole


# Dữ liệu client gửi khi thêm member vào event.
class EventStaffCreate(BaseModel):
    user_id: int
    # Mặc định MEMBER; service vẫn kiểm tra để không cho tạo OWNER tùy ý.
    role: EventStaffRole = EventStaffRole.MEMBER


# Dữ liệu trả về mô tả quan hệ user-event.
class EventStaffResponse(BaseModel):
    id: int
    event_id: int
    user_id: int
    role: EventStaffRole
    joined_at: datetime

    # Cho phép đọc dữ liệu từ SQLAlchemy EventStaff object.
    model_config = ConfigDict(from_attributes=True)
