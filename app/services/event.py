from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Event, EventStaff, EventStaffRole, User


# Lấy event chưa bị soft-delete; nếu không tồn tại trả về 404.
def get_event(event_id: int, db: Session):
    event = db.query(Event).filter(Event.id == event_id, Event.is_deleted == False).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Sự kiện không tồn tại")
    return event


# Tìm một user trong danh sách thành viên của event.
def get_member(event_id: int, user_id: int, db: Session):
    return db.query(EventStaff).filter(EventStaff.event_id == event_id, EventStaff.user_id == user_id).first()


# Kiểm tra user có phải thành viên event hay không.
def check_member(event: Event, user: User, db: Session):
    member = get_member(event.id, user.id, db)
    if member is None:
        raise HTTPException(status_code=403, detail="Bạn không phải thành viên của sự kiện")
    return member


# Kiểm tra user có phải OWNER của event hay không.
def check_owner(event: Event, user: User):
    if event.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Chỉ OWNER mới có quyền thực hiện thao tác này")


# Tạo event và đồng thời thêm người tạo vào EventStaff với role OWNER.
def create_event(data, current_user, db: Session):
    # Loại bỏ khoảng trắng đầu/cuối để tránh tên event rỗng về mặt thực tế.
    name = data.name.strip()

    if not name:
        raise HTTPException(status_code=400, detail="Tên sự kiện không được để trống")

    # Đảm bảo khoảng thời gian event hợp lệ.
    if data.start_date and data.end_date and data.end_date < data.start_date:
        raise HTTPException(status_code=400, detail="Ngày kết thúc phải sau ngày bắt đầu")

    event = Event(name=name, description=data.description, location=data.location, start_date=data.start_date, end_date=data.end_date, owner_id=current_user.id)

    db.add(event)
    # flush để database sinh event.id trước khi tạo bản ghi EventStaff.
    db.flush()

    owner = EventStaff(event_id=event.id, user_id=current_user.id, role=EventStaffRole.OWNER)

    db.add(owner)
    db.commit()
    db.refresh(event)

    return event


# Liệt kê các event mà user hiện tại tham gia.
def list_events(search, current_user, db: Session):
    query = db.query(Event).join(EventStaff, EventStaff.event_id == Event.id).filter(EventStaff.user_id == current_user.id, Event.is_deleted == False)

    if search:
        # Trim keyword trước khi tìm kiếm gần đúng theo tên event.
        search = search.strip()
        query = query.filter(Event.name.ilike("%" + search + "%"))

    # Event mới tạo được hiển thị trước.
    return query.order_by(Event.created_at.desc()).all()


# Cập nhật các field được client thực sự truyền lên.
def update_event(event, data, db: Session):
    # exclude_unset giúp PATCH chỉ thay đổi field được gửi.
    update_data = data.model_dump(exclude_unset=True)

    # Kiểm tra lại cả trường hợp start/end nằm ở dữ liệu cũ + dữ liệu mới.
    start_date = update_data.get("start_date", event.start_date)
    end_date = update_data.get("end_date", event.end_date)

    if start_date and end_date and end_date < start_date:
        raise HTTPException(status_code=400, detail="Ngày kết thúc phải sau ngày bắt đầu")

    for field, value in update_data.items():
        # Tên event không được chỉ chứa khoảng trắng.
        if field == "name":
            value = value.strip()

            if not value:
                raise HTTPException(status_code=400, detail="Tên sự kiện không được để trống")

        setattr(event, field, value)

    db.commit()
    db.refresh(event)

    return event


# Soft delete: không xóa row vật lý mà đánh dấu is_deleted.
def delete_event(event, db: Session):
    event.is_deleted = True
    event.deleted_at = datetime.now()

    db.commit()
