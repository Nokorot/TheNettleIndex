from flask import Flask

from .. import Config


def route(app: Flask):
    from .main import route

    route(app)


def construct_app(config: Config) -> Flask:
    app = Flask(__name__)

    # The secret_key is used for session encryption
    app.secret_key = config.get("APP_SECRET_KEY")

    route(app)

    # from .login import register
    # register(app)
    #
    # from .mongodb import register
    # register(app)

    return app
