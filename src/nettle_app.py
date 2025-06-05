from typing import Optional

from flask import Flask
from pyimgur import REFRESH_URL


class NettleApp:
    def __init__(self, config_file, secrets_file):
        import pyimgur

        from . import web
        from .config import Config
        from .logging import LoggerContext
        from .mongodb import MongoConnection

        self.logger = logger = LoggerContext("")
        self.config: Config = Config(logger, config_file, secrets_file)
        self.flask_app = Flask("TheNettleApp")

        # The secret_key is used for session encryption
        self.flask_app.secret_key = self.config.get("APP_SECRET_KEY")

        self.mongo_cx = MongoConnection(self)
        self.mongo_cx.connect()

        imgur_secrets: Optional[dict] = self.config.secrets.get("Imgur")
        assert imgur_secrets is not None, "Failed to find Imgur secrets"

        self.imgur = pyimgur.Imgur(
            imgur_secrets["CLIENT_ID"],
            imgur_secrets["CLIENT_SECRET"],
            access_token=imgur_secrets["ACCESS_TOKEN"],
            refresh_token=imgur_secrets["REFRESH_TOKEN"],
        )

        web.route(self)
