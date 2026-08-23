from db.database import SessionLocal
from models import User, Event, EventTask, EventStaff, UserRole, TaskStatus, TaskPriority, EventStaffRole
from core.security import get_password_hash


# Tạo dữ liệu mẫu để phục vụ development/testing.
def seed_data():
    # Mở một session độc lập vì seed chạy ngoài request của FastAPI.
    db = SessionLocal()
    try:
        # Seed User: chỉ tạo nếu email admin chưa tồn tại để script có thể chạy lại.
        user = db.query(User).filter(User.email == "admin@gmail.com").first()
        if not user:
            user = User(
                email="admin@gmail.com",
                # Không lưu password gốc; phải hash trước khi insert.
                hashed_password=get_password_hash("admin123"),
                full_name="Quản trị viên",
                role=UserRole.ADMIN
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print("Seed thành công User.")

        # Seed Event: chỉ tạo event mẫu nếu chưa có event cùng tên.
        event = db.query(Event).filter(Event.name == "Lễ kỷ niệm 5 năm").first()
        if not event:
            event = Event(
                name="Lễ kỷ niệm 5 năm",
                description="Kỷ niệm thành lập công ty",
                location="Hà Nội",
                owner_id=user.id
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            print("Seed thành công Event.")

            # Thêm user seed vào event với role OWNER.
            staff = EventStaff(event_id=event.id, user_id=user.id, role=EventStaffRole.OWNER)
            db.add(staff)

            # Tạo task mẫu thuộc event.
            task = EventTask(
                event_id=event.id,
                title="Chuẩn bị hội trường",
                description="Liên hệ đặt phòng và setup thiết bị âm thanh",
                status=TaskStatus.TODO,
                priority=TaskPriority.HIGH,
                assignee_id=user.id
            )
            db.add(task)
            db.commit()
            print("Seed thành công Staff và Task.")

    except Exception as e:
        # In lỗi để dễ phát hiện vấn đề khi chạy script seed.
        print("Lỗi seed dữ liệu:", e)
    finally:
        # Luôn đóng session dù seed thành công hay thất bại.
        db.close()


# Chỉ chạy seed khi file được thực thi trực tiếp: python app/seed.py.
if __name__ == "__main__":
    seed_data()
