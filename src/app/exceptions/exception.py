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
        http_code: Optional[int] = None,
        code: Optional[int] = None,
        message: Optional[str] = None
    ):
        self.http_code = http_code if http_code else HTTP_500_INTERNAL_SERVER_ERROR
        self.code = code if code else self.http_code
        self.message = message
    
    @staticmethod
    def bad_request_exception(message: str):
        return ChatbotException(HTTP_400_BAD_REQUEST, message=message)

    @staticmethod
    def unauthorized_exception(message: str):
        return ChatbotException(HTTP_401_UNAUTHORIZED, message=message)

    @staticmethod
    def forbiden_exception(message: str):
        return ChatbotException(HTTP_403_FORBIDDEN, message=message)

    @staticmethod
    def unprocessable_exception(message: str):
        return ChatbotException(HTTP_422_UNPROCESSABLE_ENTITY, message=message)

    @staticmethod
    def not_found_exception(message: str):
        return ChatbotException(HTTP_404_NOT_FOUND, message=message)

    @staticmethod
    def internal_error_exception(message: str):
        return ChatbotException(HTTP_500_INTERNAL_SERVER_ERROR, message=message)

    @staticmethod
    def request_entity_too_large(message: str):
        return ChatbotException(HTTP_413_REQUEST_ENTITY_TOO_LARGE, message=message)        