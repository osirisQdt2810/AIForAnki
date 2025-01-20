from app.application import get_main_application

from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

templates = Jinja2Templates(directory="app/template")

app_main = get_main_application()
app_main.mount("/storage", StaticFiles(directory="storage"), name="storage")

@app_main.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

