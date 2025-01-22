from typing import List, Annotated, Tuple, Optional, Callable, Any
from PIL import Image
from functools import wraps

from fastapi import Request, Depends

from src.engine.Chatbot import AnkiAssistant
from src.settings import settings

Error_t = Optional[str]

def lazy_load_assistant(func):
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, "assistant"):
            self.assistant = self._build_assistant()
        return func(self, *args, **kwargs)
    return wrapper

def handle_exception(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(self, *args, **kwargs) -> Tuple[Any, Error_t]:
        try:
            return (await func(self, *args, **kwargs), None)
        except Exception as e:
            return (None, str(e))
    return wrapper

class Engine(object):
    def __init__(
        self,
        lazy_loading: bool = False
    ):        
        if not lazy_loading:
            self.assistant = self._build_assistant()

    def _build_assistant(self) -> AnkiAssistant:
        return AnkiAssistant(
            device_ids=settings.GPU_DEVICES_ID,
            cache_dir=settings.CACHE_DIR,
            max_new_token_chat=settings.MAX_NEW_TOKEN_CHAT_MODEL,
            max_new_token_vl=settings.MAX_NEW_TOKEN_VISION_MODEL,
            enable_vision_model=settings.ENABLE_VISION_MODEL
        )
    
    @lazy_load_assistant
    @handle_exception
    async def answer(self, prompt: str) -> str:
        return self.assistant.answer(prompt)

    @lazy_load_assistant
    @handle_exception
    async def describe_image(self, image: Image.Image) -> str:
        return self.assistant.describe_image(image)

    @lazy_load_assistant
    @handle_exception
    async def analyse_images_with_prompt(self, images: List[Image.Image], prompt: str) -> str:
        return self.assistant.analyse_images_with_prompt(images, prompt)

    @lazy_load_assistant
    @handle_exception
    async def describe_video(self, video: str, **kwargs) -> str:
        return self.assistant.describe_video(video, **kwargs)      
    
async def get_assistant(request: Request) -> Engine:
    return request.app.anki_assistant

DepsAnkiAssistant = Annotated[Engine, Depends(get_assistant)]