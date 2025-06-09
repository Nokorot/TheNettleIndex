from .. import NettleApp


def route(app: NettleApp):
    from . import entry, main, utils

    utils.route(app)
    main.route(app)
    entry.route(app)  # api
