from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException


# Handler chuẩn hóa các lỗi HTTP thành cùng một format JSON.
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": exc.status_code,
            "message": exc.detail
        }
    )


# Handler cho lỗi validation từ request body/query/path của FastAPI/Pydantic.
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "success": False,
            "error_code": 422,
            "message": "Lỗi xác thực dữ liệu",
            # Trả chi tiết field nào không hợp lệ để client dễ sửa request.
            "details": exc.errors()
        }
    )


# Exception tùy chỉnh cho lỗi không tìm thấy resource.
class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Không tìm thấy tài nguyên"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


# Exception tùy chỉnh cho request không hợp lệ.
class BadRequestException(HTTPException):
    def __init__(self, detail: str = "Yêu cầu không hợp lệ"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
