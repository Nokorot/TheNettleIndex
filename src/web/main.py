import os
import sys

from bson import ObjectId
from flask import abort, redirect, render_template, request, url_for

from .. import NettleApp


def route(app: NettleApp):
    flask_app = app.flask_app
    logger = app.logger.sub_contex("web")

    coln = app.mongo_cx.entries_coln
    if coln is None:
        app.logger.ERROR("MongoDB collection is None")
        sys.exit(1)

    @flask_app.route("/")
    def home():
        qfilter = {}
        entries = []

        for c in coln.find(qfilter):
            _id = c.get("_id")
            str_id = str(_id)

            version = c.get("version")
            _ = version

            entries.append(
                {
                    "id": str_id,
                    "name": c.get("name"),
                    "description": c.get("description"),
                    "owner": c.get("owner"),
                    "image_url": c.get("icon_url"),
                    "time_added": c.get("added_timestamp"),
                }
            )

        return render_template("main.html", entries=entries)

    @flask_app.route("/test", methods=["GET", "POST"])
    def test():
        import datetime

        return "Welcome! The time is {}".format(str(datetime.datetime.now()))

    # @flask_app.before_request
    # def load_logged_in_user():
    #     g.user = session.get('user')
    #
    #     g.userinfo = g.user.get('userinfo') if g.user is not None else None
    #     g.user_sid = g.userinfo.get('sid') if g.userinfo is not None else None
    #     g.user_sub = g.userinfo.get('sub') if g.userinfo is not None else None
