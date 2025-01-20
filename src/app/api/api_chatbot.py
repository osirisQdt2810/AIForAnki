from typing import Annotated
from fastapi import APIRouter, Request, Response, Body

from src.app.api.api_router import TimerRoute
from src.app.models.model_chatbot import ChatRequest, ChatResponse
from src.app.core.assistant import DepsAnkiAssistant

router = APIRouter(route_class=TimerRoute)

@router.post("/answer", response_model=ChatResponse)
async def answer(
    anki_assistant: DepsAnkiAssistant,
    request: Annotated[ChatRequest, Body()] = None
) -> ChatResponse:
    pass
    