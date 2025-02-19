from typing import List, Annotated, Tuple, Optional, Callable, Any
from PIL import Image
from functools import wraps
import httpx
import io

from src.engine.chatbot import AnkiAssistant
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
    
class AsyncAPIEngine(object):
    def __init__(self):
        self.ENDPOINT_ANSWER = f"{settings.API_DOMAIN}/answer"
        self.ENDPOINT_DESCRIBE_IMAGE = f"{settings.API_DOMAIN}/describe-image"
        self.ENDPOINT_ANALYSE_IMAGES = f"{settings.API_DOMAIN}/analyse-images"
        self.ENDPOINT_DESCRIBE_VIDEO = f"{settings.API_DOMAIN}/describe-video"
        
    def answer(self, prompt: str) -> str:
        payload = {
            "prompt": prompt
        }

        # async with httpx.AsyncClient() as client:
        response = httpx.post(self.ENDPOINT_ANSWER, json=payload, timeout=None)
        response.raise_for_status()
        response.raise_for_status()
        return response.json()["data"]["answer"]
        
    async def describe_image(self, image: Image.Image) -> str:
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        image_bytes.seek(0)

        async with httpx.AsyncClient() as client:
            files = {"file": ("image.jpg", image_bytes, "image/jpeg")}
            response = await client.post(self.ENDPOINT_DESCRIBE_IMAGE, files=files)
            response.raise_for_status()
            return response.json()["data"]["answer"]

    async def analyse_images_with_prompt(self, images: List[Image.Image], prompt: str) -> str:
        files = []
        for idx, image in enumerate(images):
            image_bytes = io.BytesIO()
            image.save(image_bytes, format="JPEG")  # Save each image as JPEG
            image_bytes.seek(0)
            files.append(("files", (f"image_{idx + 1}.jpg", image_bytes, "image/jpeg")))

        data = {"prompt": prompt}

        async with httpx.AsyncClient() as client:
            response = await client.post(self.ENDPOINT_ANALYSE_IMAGES, data=data, files=files)
            response.raise_for_status()
            return response.text

    async def describe_video(self, video: str, **kwargs) -> str:
        async with httpx.AsyncClient() as client:
            with open(video, "rb") as file:
                files = {"file": (video.split("/")[-1], file, "video/mp4")}
                response = await client.post(self.ENDPOINT_DESCRIBE_VIDEO, files=files, params=kwargs)
                response.raise_for_status()
                return response.text