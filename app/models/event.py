from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base


# Model đại diện cho một sự kiện trong hệ thống.
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    location = Column(String(255))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    # Liên kết event với user tạo/sở hữu event.
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    # Soft delete: giữ dữ liệu nhưng đánh dấu đã xóa.
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    # Người tạo/sở hữu sự kiện.
    owner = relationship("User", back_populates="events_owned", foreign_keys=[owner_id])
    # Danh sách thành viên tham gia event thông qua EventStaff.
    staffs = relationship("EventStaff", back_populates="event")
    # Danh sách task thuộc event.
    tasks = relationship("EventTask", back_populates="event")
