import logging
import logging.config

from src.settings import settings, PROJECT_SOURCE_DIR

__all__ = ["logger"]

logging.config.fileConfig(f"{PROJECT_SOURCE_DIR}/{settings.LOGGING_CONFIG_FILE}", disable_existing_loggers=False)
logger = logging.getLogger("app")