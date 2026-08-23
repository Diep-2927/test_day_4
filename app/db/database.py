from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

# Engine quản lý kết nối giữa SQLAlchemy và database.
engine = create_engine(settings.DATABASE_URL)

# Factory tạo một database session mới cho mỗi request/operation.
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

# Base class để các SQLAlchemy model kế thừa và được metadata quản lý.
Base = declarative_base()


# Dependency của FastAPI: mở session, cung cấp cho endpoint rồi luôn đóng session.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        # Đảm bảo giải phóng connection kể cả khi request phát sinh exception.
        db.close()
