from flask import Flask


class NettleApp:
    def __init__(self):

        from .logging import LoggerContext

        self.logger = LoggerContext("")

        from .config import Config, construct_config

        self.config: Config = construct_config()

        self.flask_app = Flask("TheNettleApp")

        # The secret_key is used for session encryption
        self.flask_app.secret_key = self.config.get("APP_SECRET_KEY")

        from .mongodb import MongoConnection

        self.mongo_cx = MongoConnection(self)
        self.mongo_cx.connect()

        from .web import route

        route(self)
        # self.flask_app: Flask = construct_flask_app(self)
