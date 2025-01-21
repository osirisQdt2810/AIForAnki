from typing import Optional, List, ClassVar

from dynaconf import Dynaconf
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

dyna_settings = Dynaconf(
    settings_file=["config/settings.toml", "config/.secret.toml"],
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
    GPU_DEVICES_ID: Optional[List[int]] = Field()
    MAX_NEW_TOKEN_CHAT_MODEL: Optional[int] = Field()
    MAX_NEW_TOKEN_VISION_MODEL: Optional[int] = Field()
    ENABLE_VISION_MODEL: Optional[bool] = Field()
    CACHE_DIR: Optional[str] = Field()
    
class AppSettings(CommonSettings, ServerSettings, ChatbotSettings):
    config: ClassVar[SettingsConfigDict] = SettingsConfigDict(extra="ignore")
    
settings = AppSettings.model_validate(dyna_settings.as_dict())