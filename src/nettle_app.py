from flask import Flask


class NettleApp:
    def __init__(self):
        from . import web
        from .config import Config, construct_config
        from .logging import LoggerContext
        from .mongodb import MongoConnection

        self.logger = logger = LoggerContext("")
        self.config: Config = construct_config(logger)
        self.flask_app = Flask("TheNettleApp")

        # The secret_key is used for session encryption
        self.flask_app.secret_key = self.config.get("APP_SECRET_KEY")

        self.mongo_cx = MongoConnection(self)
        self.mongo_cx.connect()

        web.route(self)
