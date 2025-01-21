from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from src.app.exceptions.exception import ChatbotException
from src.app.logging.logger import logger
from src.app.models.model_http_response import ResponseMessage

class ValidationExceptionHandler:
    async def __call__(self, request: Request, exception: RequestValidationError):
        logger.error(
            str(jsonable_encoder({
                "detail": exception.errors(), 
                "body": exception.body
            }))
        )
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder(
                ResponseMessage().message(
                    code=HTTP_422_UNPROCESSABLE_ENTITY,
                    msg=ValidationExceptionHandler.get_message_validation(exception)
                )
            )
        )
        
    @staticmethod
    def get_message_validation(exception: RequestValidationError):
        message = ""
        for error in exception.errors():
            message += "/'" + str(error["loc"][1]) + "'/" + ": " + error["msg"] + ", "

        message = message[:-2]

        return message
        
class ChatbotExceptionHandler:
    async def __call__(self, request: Request, exception: ChatbotException):
        logger.error(
            str(jsonable_encoder(
                ResponseMessage().message(
                    code=exception.code,
                    msg=exception.message
                )
            ))
        )
        return JSONResponse(
            status_code=exception.http_code,
            content=jsonable_encoder(
                ResponseMessage().message(
                    code=exception.code,
                    msg=exception.message
                )
            )
        )
