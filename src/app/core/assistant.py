from typing import List, Annotated
from PIL import Image

from fastapi import Request, Depends

from src.engine.Chatbot import AnkiAssistant
from src.app import settings

class Engine(object):
    def __init__(
        self,
        lazy_loading: bool = False
    ):        
        if not lazy_loading:
            self.assistant = self._build_assistant()

    @staticmethod
    def _ensure_assistant(func):
        def wrapper(self, *args, **kwargs):
            if not hasattr(self, "assistant"):
                self.assistant = self._build_assistant()
            return func(self, *args, **kwargs)
        return wrapper
    
    def _build_assistant(self) -> AnkiAssistant:
        return AnkiAssistant(
            device_ids=settings.GPU_DEVICES_ID,
            max_new_token_chat=settings.MAX_NEW_TOKEN_CHAT_MODEL,
            max_new_token_vl=settings.MAX_NEW_TOKEN_VISION_MODEL,
            enable_vision_model=settings.ENABLE_VISION_MODEL
        )
    
    @_ensure_assistant
    def answer(self, prompt: str) -> str:
        return self.assistant.answer(prompt)
    
    @_ensure_assistant
    def describe_image(self, image: Image.Image) -> List[str]:
        return self.assistant.describe_image(image)
    
    @_ensure_assistant
    def analyse_images_with_prompt(self, images: List[Image.Image], prompt: str) -> str:
        return self.assistant.analyse_images_with_prompt(images, prompt)
    
    @_ensure_assistant
    def describe_video(self, video: str, **kwargs) -> str:
        return self.assistant.describe_video(video)
    
async def get_assistant(request: Request) -> Engine:
    return request.app.anki_assistant

DepsAnkiAssistant = Annotated[Engine, Depends(get_assistant)]