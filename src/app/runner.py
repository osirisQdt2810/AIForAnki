from src.app.application import get_main_application

from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

templates = Jinja2Templates(directory="src/app/template")

main_app = get_main_application()
# main_app.mount("/storage", StaticFiles(directory="storage"), name="storage")

@main_app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

