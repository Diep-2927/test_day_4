from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from db.database import get_db
from models import User
from schemas import UserCreate, UserResponse, UserLogin
from schemas.token import Token
from core.security import get_password_hash, verify_password, create_access_token
from core.config import settings
from enum import Enum

# Router chứa các endpoint đăng ký và đăng nhập.
router = APIRouter(prefix="/auth", tags=["Authentication"])


# Đăng ký user mới và lưu password dưới dạng hash.
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Kiểm tra email đã tồn tại để tránh duplicate account.
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email này đã tồn tại")

    # Hash password trước khi lưu database.
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Đăng nhập: xác thực email/password rồi cấp JWT access token.
@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    # Tìm user theo email.
    user = db.query(User).filter(User.email == data.email).first()

    # Không tiết lộ email hay password nào sai để tránh lộ thông tin account.
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản hoặc mật khẩu không chính xác"
        )

    # Tài khoản bị khóa không được đăng nhập.
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Tài khoản đã bị vô hiệu hóa")

    # Enum cần lấy .value để đưa giá trị chuỗi vào JWT.
    if isinstance(user.role, Enum):
        role_value = user.role.value
    else:
        role_value = user.role

    # Thời gian hết hạn token lấy từ cấu hình.
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Đưa các claim cần thiết vào token; sub là email dùng để xác định user.
    access_token = create_access_token(
        data={
            "sub": user.email,
            "id": user.id,
            "full_name": user.full_name,
            "role": role_value
        },
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
