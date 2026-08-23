from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from db.database import get_db
from dependencies.auth import get_current_active_user
from models import User, TaskStatus, TaskPriority
from schemas.event_task import EventTaskCreate, EventTaskUpdate, EventTaskResponse
from services import event, event_task

# Router quản lý task thuộc event.
router = APIRouter(prefix="/events", tags=["Event Tasks"])


# Thành viên event có thể tạo task.
@router.post("/{event_id}/event-tasks", response_model=EventTaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(event_id: int, data: EventTaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    event_obj = event.get_event(event_id, db)
    # Phải là member của event mới được tạo task.
    event.check_member(event_obj, current_user, db)
    return event_task.create_task(event_obj.id, data, db)


# Lấy danh sách task với filter, sort và pagination.
@router.get("/{event_id}/event-tasks", response_model=List[EventTaskResponse])
def list_tasks(event_id: int, search: Optional[str] = Query(None, max_length=255), task_status: Optional[TaskStatus] = Query(None, alias="status"), priority: Optional[TaskPriority] = None, assignee_id: Optional[int] = None, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100), sort_by: str = Query("created_at"), sort_order: str = Query("desc"), db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    event_obj = event.get_event(event_id, db)
    event.check_member(event_obj, current_user, db)

    # Router nhận/validate tham số, service thực hiện query database.
    return event_task.list_tasks(
        event_obj.id,
        search,
        task_status,
        priority,
        assignee_id,
        page,
        size,
        sort_by,
        sort_order,
        db
    )


# Xem chi tiết task; người xem phải thuộc event chứa task.
@router.get("/event-tasks/{task_id}", response_model=EventTaskResponse)
def get_task_detail(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    task = event_task.get_task(task_id, db)
    event_obj = event.get_event(task.event_id, db)
    event.check_member(event_obj, current_user, db)
    return task


# OWNER hoặc người được giao task mới được cập nhật task.
@router.patch("/event-tasks/{task_id}", response_model=EventTaskResponse)
def update_task(task_id: int, data: EventTaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    task = event_task.get_task(task_id, db)
    event_obj = event.get_event(task.event_id, db)

    # Kiểm tra quyền riêng của task trước khi cập nhật.
    event_task.check_task_permission(task, event_obj, current_user)

    return event_task.update_task(task, event_obj, data, db)


# Chỉ OWNER mới được xóa task.
@router.delete("/event-tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    task = event_task.get_task(task_id, db)
    event_obj = event.get_event(task.event_id, db)
    event.check_owner(event_obj, current_user)
    event_task.delete_task(task, db)
    return None
