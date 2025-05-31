from .. import Config, LoggerContext, NettleApp


def route(app: NettleApp):
    from .main import route

    route(app)
