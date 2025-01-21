from fastapi import APIRouter

from src.app.api import api_chatbot

__all__ = [
    "router"
]

router = APIRouter()
router.include_router(api_chatbot.router, prefix="/llm", tags=["llm"])