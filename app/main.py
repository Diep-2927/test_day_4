from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from db.database import engine
from core.exceptions import custom_http_exception_handler, validation_exception_handler
import models
from routers import auth, users, event, event_task

# Tự động tạo các bảng từ SQLAlchemy model nếu database chưa có.
models.Base.metadata.create_all(bind=engine)

# Khởi tạo ứng dụng FastAPI và đặt tên hiển thị cho API.
app = FastAPI(title="Event Management API")

# Đăng ký các nhóm API: xác thực, người dùng, sự kiện và công việc.
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(event.router)
app.include_router(event_task.router)

# Chuẩn hóa response khi xảy ra lỗi HTTP (400, 401, 403, 404...).
app.add_exception_handler(HTTPException, custom_http_exception_handler)

# Chuẩn hóa lỗi dữ liệu đầu vào do Pydantic/FastAPI phát hiện.
app.add_exception_handler(RequestValidationError, validation_exception_handler)


# Endpoint kiểm tra nhanh server có đang chạy hay không.
@app.get("/test")
def test():
    return {"message": "API đang hoạt động ổn định"}
