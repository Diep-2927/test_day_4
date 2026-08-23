from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from db.database import get_db
from dependencies.auth import get_current_active_user
from models import User
from schemas.event import EventCreate, EventResponse, EventUpdate
from schemas.event_staff import EventStaffCreate, EventStaffResponse
from services import event, event_member

# Router cho event và thành viên của event.
router = APIRouter(prefix="/events", tags=["Events"])


# Tạo event mới; service sẽ kiểm tra dữ liệu và tạo OWNER.
@router.post("/", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(data: EventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return event.create_event(data, current_user, db)


# Lấy các event mà user hiện tại là thành viên, có thể tìm theo tên.
@router.get("/", response_model=List[EventResponse])
def list_events(search: Optional[str] = Query(None, max_length=255), db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return event.list_events(search, current_user, db)


# Xem chi tiết event; chỉ thành viên của event mới được truy cập.
@router.get("/{event_id}", response_model=EventResponse)
def get_event_detail(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    event_obj = event.get_event(event_id, db)
    event.check_member(event_obj, current_user, db)
    return event_obj


# Cập nhật event; chỉ OWNER được phép sửa.
@router.patch("/{event_id}", response_model=EventResponse)
def update_event(event_id: int, data: EventUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    event_obj = event.get_event(event_id, db)
    event.check_owner(event_obj, current_user)
    return event.update_event(event_obj, data, db)


# Soft-delete event; chỉ OWNER được phép xóa.
@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    event_obj = event.get_event(event_id, db)
    event.check_owner(event_obj, current_user)
    event.delete_event(event_obj, db)
    return None


# OWNER thêm một user vào event.
@router.post("/{event_id}/members", response_model=EventStaffResponse, status_code=status.HTTP_201_CREATED)
def add_member(event_id: int, data: EventStaffCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    event_obj = event.get_event(event_id, db)
    event.check_owner(event_obj, current_user)
    return event_member.add_member(event_obj, data, db)


# Thành viên có thể xem danh sách thành viên của event.
@router.get("/{event_id}/members", response_model=List[EventStaffResponse])
def list_members(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    event_obj = event.get_event(event_id, db)
    event.check_member(event_obj, current_user, db)
    return event_member.list_members(event_obj.id, db)


# OWNER xóa một MEMBER khỏi event.
@router.delete("/{event_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(event_id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    event_obj = event.get_event(event_id, db)
    event.check_owner(event_obj, current_user)
    event_member.remove_member(event_obj, user_id, db)
    return None
