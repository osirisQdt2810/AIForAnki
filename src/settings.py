import os

from typing import Optional, List, ClassVar

from dynaconf import Dynaconf
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_SOURCE_DIR = os.path.dirname(os.path.dirname(__file__))
dyna_settings = Dynaconf(
    settings_file=[
        f"{PROJECT_SOURCE_DIR}/config/settings.toml", 
        f"{PROJECT_SOURCE_DIR}/config/.secret.toml"
    ],
    environments=True
)

class CommonSettings(BaseSettings):
    PROJECT_NAME: Optional[str] = Field()
    API_PREFIX: Optional[str] = Field()
    LOGGING_CONFIG_FILE: Optional[str] = Field()
    
class ServerSettings(BaseSettings):
    BACKEND_CORS_ORIGINS: Optional[str] = Field()
    SERVER_NAME: Optional[str] = Field()
    SERVER_HOST: Optional[str] = Field()
    SERVER_STATIC_HOST: Optional[str] = Field()
    SERVER_PORT: Optional[int] = Field()
    SENTRY_DNS: Optional[str] = Field()
    WORKERS: Optional[int] = Field()
    DEBUG: Optional[bool] = Field(default=True)

class ChatbotSettings(BaseSettings):
    LAZY_LOADING: Optional[bool] = Field()
    GPU_DEVICES_ID: Optional[List[int]] = Field()
    MAX_NEW_TOKEN_CHAT_MODEL: Optional[int] = Field()
    MAX_NEW_TOKEN_VISION_MODEL: Optional[int] = Field()
    ENABLE_VISION_MODEL: Optional[bool] = Field()
    CACHE_DIR: Optional[str] = Field()
    CHAT_MODEL_NAME: Optional[str] = Field()
    VISION_MODEL_NAME: Optional[str] = Field()
    DISTRIBUTED: Optional[bool] = Field()

class AnkiSettings(BaseSettings):
    API_DOMAIN: Optional[str] = Field()

class AppSettings(CommonSettings, ServerSettings, ChatbotSettings, AnkiSettings):
    config: ClassVar[SettingsConfigDict] = SettingsConfigDict(extra="ignore")
    
settings = AppSettings.model_validate(dyna_settings.as_dict())