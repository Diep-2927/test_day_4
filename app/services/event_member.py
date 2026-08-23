from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import EventStaff, EventStaffRole, User


# Thêm một user vào danh sách thành viên của event.
def add_member(event, data, db: Session):
    # Owner đã được tạo tự động khi tạo event nên không được thêm lại.
    if data.user_id == event.owner_id:
        raise HTTPException(status_code=400, detail="Owner đã là thành viên của sự kiện")

    # Không cho phép client tự tạo thêm OWNER.
    if data.role == EventStaffRole.OWNER:
        raise HTTPException(status_code=400, detail="Không thể thêm thành viên với role OWNER")

    # User phải tồn tại.
    user = db.query(User).filter(User.id == data.user_id).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User không tồn tại")

    # Không thêm tài khoản đang bị khóa.
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Không thể thêm tài khoản đang bị khóa")

    # Tránh một user xuất hiện nhiều lần trong cùng event.
    existing_member = db.query(EventStaff).filter(EventStaff.event_id == event.id, EventStaff.user_id == user.id).first()

    if existing_member:
        raise HTTPException(status_code=400, detail="User đã là thành viên của sự kiện")

    # Role thực tế luôn là MEMBER, không tin role từ client để tạo OWNER.
    member = EventStaff(event_id=event.id, user_id=user.id, role=EventStaffRole.MEMBER)

    db.add(member)
    db.commit()
    db.refresh(member)

    return member


# Lấy danh sách thành viên của event, sắp xếp theo thời điểm tham gia.
def list_members(event_id, db: Session):
    return db.query(EventStaff).filter(EventStaff.event_id == event_id).order_by(EventStaff.joined_at).all()


# Xóa một member khỏi event.
def remove_member(event, user_id, db: Session):
    member = db.query(EventStaff).filter(EventStaff.event_id == event.id, EventStaff.user_id == user_id).first()

    if member is None:
        raise HTTPException(status_code=404, detail="User không phải thành viên của sự kiện")

    # Owner không thể bị xóa khỏi event bằng API này.
    if member.role == EventStaffRole.OWNER:
        raise HTTPException(status_code=400, detail="Không thể xóa OWNER khỏi sự kiện")

    db.delete(member)
    db.commit()
