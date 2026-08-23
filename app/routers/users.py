from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from db.database import get_db
from models import User
from schemas import UserResponse
from dependencies.auth import get_current_active_user, get_admin_user

# Router quản lý thông tin user.
router = APIRouter(prefix="/users", tags=["Users"])


# Lấy thông tin của chính user đang đăng nhập.
@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


# ADMIN có thể lấy danh sách user và lọc theo keyword/trạng thái active.
@router.get("/", response_model=List[UserResponse])
def get_users(
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    # Dependency này đồng thời kiểm tra token, active account và role ADMIN.
    current_user: User = Depends(get_admin_user)
):
    query = db.query(User)

    # Tìm gần đúng theo email hoặc họ tên, không phân biệt hoa thường.
    if search:
        query = query.filter(
            (User.email.ilike(f"%{search}%")) |
            (User.full_name.ilike(f"%{search}%"))
        )

    # Chỉ thêm filter nếu client thực sự truyền is_active.
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    return query.all()
