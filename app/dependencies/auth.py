from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.orm import Session
from core.config import settings
from db.database import get_db
from models import User, UserRole
from schemas.token import TokenData

# HTTPBearer yêu cầu client gửi token theo dạng: Authorization: Bearer <token>.
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    # Lấy JWT thực tế từ header Authorization.
    token = credentials.credentials

    # Lỗi dùng chung khi token sai, hết hạn hoặc user không tồn tại.
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin (Token sai hoặc hết hạn)"
    )
    try:
        # Giải mã và kiểm tra chữ ký + thời hạn của JWT.
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # sub chứa email được tạo lúc login.
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except jwt.InvalidTokenError:
        raise credentials_exception

    # Tìm user tương ứng với email trong database.
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    # User hợp lệ nhưng đã bị khóa thì vẫn không được sử dụng API yêu cầu active account.
    if not current_user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Tài khoản đã bị khóa"
        )
    return current_user


def get_admin_user(current_user: User = Depends(get_current_active_user)):
    # Chỉ tài khoản có role ADMIN mới qua được dependency này.
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Không có quyền truy cập (Yêu cầu ADMIN)"
        )
    return current_user
