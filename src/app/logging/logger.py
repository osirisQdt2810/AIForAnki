import logging
import logging.config

from app import settings

__all__ = ["logger"]

logging.config.fileConfig(settings.LOGGING_CONFIG_FILE, disable_existing_loggers=False)
logger = logging.getLogger("app")