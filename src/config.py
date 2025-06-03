import os
from typing import Any, Optional

from dotenv import load_dotenv

from src.logging import LoggerContext


class Config:
    UPLOAD_FOLDER: Optional[str] = None
    ICON_FOLDER: Optional[str] = None

    def __init__(self, logger):
        self.logger = logger.sub_contex("config")

    def get_env(self, key: str, default=None):
        value = os.environ.get(key, default)
        if not value:
            self.logger.ERROR('Environment variable "%s" is not declared', key)

        return value

    def get(self, key: str) -> Any:
        return self.get_env(key)


def construct_config(logger: LoggerContext) -> Config:
    load_dotenv(dotenv_path=".env")
    return Config(logger)
