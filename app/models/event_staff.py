from datetime import datetime
import enum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from db.database import Base


# Role của user bên trong một event.
class EventStaffRole(str, enum.Enum):
    OWNER = "OWNER"
    MEMBER = "MEMBER"


# Bảng trung gian liên kết User và Event, đồng thời lưu role/thời điểm tham gia.
class EventStaff(Base):
    __tablename__ = "event_staffs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # Khóa ngoại tới event và user.
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    # Mặc định thành viên mới là MEMBER.
    role = Column(Enum(EventStaffRole), default=EventStaffRole.MEMBER, nullable=False)
    joined_at = Column(DateTime, default=datetime.now)

    # Quan hệ ngược về Event và User.
    event = relationship("Event", back_populates="staffs")
    user = relationship("User", back_populates="events_involved")
