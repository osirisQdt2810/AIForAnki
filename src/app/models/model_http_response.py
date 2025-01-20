from typing import Optional, TypeVar, Generic

from pydantic import BaseModel

T = TypeVar("T")

class ResponseMessage(BaseModel):
    code: Optional[int] = None
    http_code: Optional[int] = None
    msg: Optional[str] = None
    
    def message(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        return self
    
    def success_message(self):
        self.code = 0
        self.msg = "Successful"
        return self
    
class ResponseData(ResponseMessage, Generic[T]):
    data: Optional[T] = None
    
    class Config:
        arbitrary_types_allowed = True
        
    def message(self, code: int, msg: str, data: T):
        self.code = code
        self.msg = msg
        self.data = data
        return self
    
    def success_message(self, data: T):
        super().success_message()(self)
        self.data = data
        return self
    
    