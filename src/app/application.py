from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from src.settings import settings
from src.app.api import router
from src.app.context import AppLifecycle
from src.app.exceptions.exception import ChatbotException
from src.app.exceptions.exception_handlers import ChatbotExceptionHandler, ValidationExceptionHandler
        
def get_main_application() -> FastAPI:
    # setup main application
    async def lifespan(app: FastAPI):
        async with AppLifecycle(app):
            yield
            
    main_app = FastAPI(
        title=settings.PROJECT_NAME,
        docs_url="/docs",
        redoc_url="/re-docs",
        openapi_url=settings.API_PREFIX + "/openapi.json",
        description="AFA Server",
        lifespan=lifespan
    )
    
    # CORS
    origins = ["*"]
    if settings.BACKEND_CORS_ORIGINS:
        origins.extend([
            origin.strip() 
            for origin in settings.BACKEND_CORS_ORIGINS.split(",")
        ])
        
        main_app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
        
    # setup exceptions
    main_app.add_exception_handler(RequestValidationError, ValidationExceptionHandler())
    main_app.add_exception_handler(ChatbotException, ChatbotExceptionHandler())
    
    # setup router
    main_app.include_router(router, prefix=settings.API_PREFIX)
    
    return main_app
            

    