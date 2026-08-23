from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Xác định thư mục gốc của project để tìm file .env.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"


# Class cấu hình tập trung cho toàn bộ ứng dụng.
class Settings(BaseSettings):
    # Tên project dùng cho cấu hình/hiển thị.
    PROJECT_NAME: str = "FastAPI Event Management"
    # Chuỗi kết nối database lấy từ biến môi trường/.env.
    DATABASE_URL: str
    # Secret dùng để ký và kiểm tra JWT.
    SECRET_KEY: str
    # Thuật toán ký JWT mặc định.
    ALGORITHM: str = "HS256"
    # Thời gian sống của access token tính bằng phút.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Cho phép Pydantic Settings đọc biến cấu hình từ file .env.
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8"
    )


# Tạo một instance dùng chung trong toàn bộ ứng dụng.
settings = Settings()
