from flask import Flask


class NettleApp:
    def __init__(self, config_file, secrets_file):
        from . import web
        from .config import Config
        from .imgur import MyImgur
        from .logging import LoggerContext
        from .mongodb import MongoConnection

        self.logger = logger = LoggerContext("")
        self.config: Config = Config(logger, config_file, secrets_file)
        self.flask_app = Flask("TheNettleApp")

        # The secret_key is used for session encryption
        self.flask_app.secret_key = self.config.get("APP_SECRET_KEY")

        self.mongo_cx = MongoConnection(self)
        self.mongo_cx.connect()

        self.imgur = MyImgur(self)

        web.route(self)
