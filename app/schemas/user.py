from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from models.user import UserRole


# Các field dùng chung của user và response.
class UserBase(BaseModel):
    # EmailStr giúp Pydantic kiểm tra format email.
    email: EmailStr
    full_name: str = None
    is_active: bool = True


# Schema request đăng ký user; password chỉ xuất hiện ở input.
class UserCreate(UserBase):
    password: str


# Schema request đăng nhập.
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Schema trả về client; không trả hashed_password để tránh lộ thông tin nhạy cảm.
class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime

    # Cho phép tạo response từ SQLAlchemy User object.
    model_config = ConfigDict(from_attributes=True)
