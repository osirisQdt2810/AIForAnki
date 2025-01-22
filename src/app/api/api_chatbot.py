import io
import os

from typing import Annotated, List
from fastapi import APIRouter, Body, UploadFile, File
from PIL import Image

from src.app.api.api_router import TimerRoute
from src.app.models.model_chatbot import ChatResponse
from src.app.models.model_http_response import ResponseData
from src.app.core.assistant import DepsAnkiAssistant
from src.app.exceptions.exception import ChatbotException
from src.helpers.logging.logger import logger
from src.settings import settings

router = APIRouter(route_class=TimerRoute)

@router.post("/answer", response_model=ResponseData)
async def answer(
    anki_assistant: DepsAnkiAssistant,
    prompt: str = Body(...)
) -> ResponseData:
    # run assistant
    answer, error = await anki_assistant.answer(prompt)
    
    if error:
        raise ChatbotException.unprocessable_exception(message=str(error))
    
    return ResponseData().success_message(
        data=ChatResponse(answer=answer)
    )

@router.post("/describe-image", response_model=ResponseData)
async def answer(
    anki_assistant: DepsAnkiAssistant,
    file: UploadFile = File(...)
) -> ResponseData:
    # read image
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))
    
    # run assistant
    desc, error = await anki_assistant.describe_image(image)
    if error:
        raise ChatbotException.unprocessable_exception(message=str(error))
    
    return ResponseData().success_message(
        data=ChatResponse(answer=desc)
    )
    
@router.post("/analyse-images", response_model=ResponseData)
async def answer(
    anki_assistant: DepsAnkiAssistant,
    prompt: str = Body(...),
    files: List[UploadFile] = File(...)
) -> ResponseData:    
    # read and convert all files into PIL Images
    images = []
    for file in files:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        images.append(image)

    # analyse images using the assistant
    anal, error = await anki_assistant.analyse_images_with_prompt(images, prompt)
    if error:
        raise ChatbotException.unprocessable_exception(message=str(error))
    
    return ResponseData().success_message(
        data=ChatResponse(answer=anal)
    )

    
@router.post("/describe-video", response_model=ResponseData)
async def answer(
    anki_assistant: DepsAnkiAssistant,
    file: UploadFile = File(...)
) -> ResponseData:
    # Save uploaded file to a temporary location
    uploaded_dir = f"{settings.CACHE_DIR}/uploaded_videos/"; os.makedirs(uploaded_dir, exist_ok=True)
    temp_video_path = f"{uploaded_dir}/{file.filename}"
    with open(temp_video_path, "wb") as f:
        f.write(await file.read())

    # Call the describe_video method
    desc, error = await anki_assistant.describe_video(temp_video_path)

    # Handle errors
    if error:
        raise ChatbotException.unprocessable_exception(message=str(error))

    return ResponseData().success_message(
        data=ChatResponse(answer=desc)
    )