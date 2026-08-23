import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime


# Các role cấp hệ thống của user.
class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"


# SQLAlchemy model đại diện cho bảng users.
class User(Base):
    __tablename__ = "users"

    # Khóa chính tự tăng.
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    # Email duy nhất, đồng thời được dùng để đăng nhập.
    email = Column(String(255), unique=True, index=True, nullable=False)
    # Chỉ lưu password đã hash, không lưu password gốc.
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    # False nghĩa là tài khoản bị khóa/vô hiệu hóa.
    is_active = Column(Boolean, default=True)
    # Role mặc định là USER.
    role = Column(Enum(UserRole), default=UserRole.USER)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # Một user có thể sở hữu nhiều event.
    events_owned = relationship("Event", back_populates="owner", foreign_keys="Event.owner_id")
    # User có thể tham gia nhiều event thông qua bảng trung gian EventStaff.
    events_involved = relationship("EventStaff", back_populates="user")
    # User có thể được giao nhiều task.
    tasks_assigned = relationship("EventTask", back_populates="assignee")
