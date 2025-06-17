import os
from typing import Any, Optional

from pytoml import TomlError

from src.logging import LoggerContext


class MissingConfigError(Exception):
    """Raised when a required config value is missing."""

    def __init__(self, key, message=None):
        if message is None:
            message = f"Missing required configuration key: '{key}'"
        super().__init__(message)
        self.key = key


class Config:
    UPLOAD_FOLDER: Optional[str] = None
    ICON_FOLDER: Optional[str] = None

    def __init__(self, logger: LoggerContext, cnf_file: str, secrets_file: str):
        def read_toml(fname):
            import pytoml  # type: ignore

            with open(fname, "rb") as fin:
                try:
                    return pytoml.load(fin)
                except TomlError as e:
                    print("Toml Error: ", e)
                    exit(1)

        self.config_file = cnf_file
        self.cnf = read_toml(cnf_file)

        self.secrets_file = secrets_file
        self.secrets: dict = read_toml(secrets_file)

        self.logger = logger.sub_contex("config")

    def get_env(self, key: str, default=None):
        value = os.environ.get(key, default)
        if not value:
            raise MissingConfigError(
                key, message=f"Expected environment variable '{key}' is missing"
            )
        return value

    def get(self, key: str, default=None) -> Any:
        val = self.cnf.get(key)
        if val is not None:
            return val
        return default

    def __getitem__(self, key):
        value = self.get(key)
        if value is None:
            raise MissingConfigError(key)
        return value
