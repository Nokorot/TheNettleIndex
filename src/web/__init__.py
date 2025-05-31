from .. import Config, LoggerContext, NettleApp


def route(app: NettleApp):
    from .utils import route

    route(app)

    from .main import route

    route(app)
