from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from app import settings

@asynccontextmanager
async def lifespan(main_app: FastAPI):
    # await init()
    # await start()
    # yield
    # await stop()
    pass

def get_main_application() -> FastAPI:
    # setup main application
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
    main_app.add_exception_handler(RequestValidationError, ValidationExceptionHandler)
    main_app.add_exception_handler(LogicError, LogicExceptionHandler)
    
    # setup router
    main_app.include_router(api_router, prefix=settings.API_PREFIX)
    
    return main_app
            

    