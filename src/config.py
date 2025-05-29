import os

from dotenv import load_dotenv  # type: ignore

# from .logging import getLogger


class Config:
    def __init__(self):
        pass

    def get_env(self, key, default=None):
        value = os.environ.get(key, default)
        if not value:
            logger.ERROR('Environment variable "%s" is not declared', key)

        return value

    def get(self, key):
        self.get_env(key)


def construct_config() -> Config:
    load_dotenv(dotenv_path=".env")
    return Config()
