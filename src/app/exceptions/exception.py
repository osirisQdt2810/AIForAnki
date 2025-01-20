from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_413_REQUEST_ENTITY_TOO_LARGE,
)

from typing import Optional

class ChatbotException(Exception):
    http_code: int
    code: int
    message: str
    
    def __init__(
        self,
        code: Optional[int] = None,
        message: Optional[str] = None
    ):
        self.code = code
        self.message = message