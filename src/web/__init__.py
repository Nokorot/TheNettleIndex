from .. import NettleApp


def route(app: NettleApp):
    from . import main, utils

    utils.route(app)
    main.route(app)
