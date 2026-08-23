import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from .config import settings


# Hash mật khẩu trước khi lưu vào database; không lưu plaintext password.
def get_password_hash(password: str) -> str:
    # Chuyển password từ string sang bytes vì bcrypt làm việc với bytes.
    pwd_bytes = password.encode("utf-8")
    # Tạo salt ngẫu nhiên để mỗi password có hash khác nhau.
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)

    # Chuyển hash bytes về string để dễ lưu vào database.
    return hashed_password.decode("utf-8")


# Kiểm tra password người dùng nhập có khớp với hash đã lưu hay không.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    pass_bytes = plain_password.encode("utf-8")
    hashed_pw_bytes = hashed_password.encode("utf-8")

    return bcrypt.checkpw(pass_bytes, hashed_pw_bytes)


# Tạo JWT access token chứa thông tin cần thiết để xác thực request.
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    # Copy để không làm thay đổi dictionary gốc được truyền vào.
    to_encode = data.copy()

    # Xác định thời điểm token hết hạn; mặc định 15 phút nếu không truyền thời gian.
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    # Thêm claim exp để JWT tự hết hạn.
    to_encode.update({"exp": expire})
    # Ký JWT bằng SECRET_KEY và thuật toán cấu hình trong settings.
    encode_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encode_jwt
