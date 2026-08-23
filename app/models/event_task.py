from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from db.database import Base


# Trạng thái vòng đời của task.
class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


# Mức độ ưu tiên của task.
class TaskPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# Model đại diện cho công việc thuộc một event.
class EventTask(Base):
    __tablename__ = "event_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Task bắt buộc phải thuộc một event.
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    # Có thể chưa giao task cho ai nên assignee_id cho phép NULL.
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # Quan hệ task -> event.
    event = relationship("Event", back_populates="tasks")
    # Quan hệ task -> user được giao.
    assignee = relationship("User", back_populates="tasks_assigned")
