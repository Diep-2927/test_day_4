from pydantic import BaseModel


# Schema response khi login thành công.
class Token(BaseModel):
    access_token: str
    token_type: str


# Dữ liệu tối thiểu trích xuất từ JWT sau khi decode.
class TokenData(BaseModel):
    # Email lấy từ claim "sub" để truy vấn User.
    email: str | None = None
