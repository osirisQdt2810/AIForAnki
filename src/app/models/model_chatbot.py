from typing import Optional

from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    prompt: str = Field()
    
class ChatResponse(BaseModel):
    answer: str = Field()