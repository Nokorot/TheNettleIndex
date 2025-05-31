from flask import render_template, request, send_file, url_for

from .. import NettleApp


def route(app: NettleApp):
    flask_app = app.flask_app

    coln = app.mongo_cx.entries_coln

    @flask_app.route("/")
    def home():
        qfilter = {}
        entries = []

        for c in coln.find(qfilter):

            id = str(c.get("_id"))
            entries.append(
                {
                    "id": id,
                    "name": c.get("name"),
                    "description": c.get("description"),
                    "owner": "Alice",
                    "image_url": url_for("entry_icon", entry_id=id),
                    "time_added": c.get("added_timestamp"),
                }
            )

        from datetime import datetime, timedelta

        for i in range(100):
            entries.append(
                {
                    "id": i,
                    "name": "Object nr. %d" % i,
                    "description": f"This is the {i}'th generated example entry",
                    "owner": "Name nr. %s" % i,
                    "image_url": url_for("entry_icon", entry_id=i),
                    "time_added": (
                        datetime.now() - timedelta(hours=i * 10)
                    ).timestamp(),
                }
            )

        return render_template("main.html", entries=entries)

    @flask_app.route("/media/entry-icon", methods=["GET"])
    def entry_icon():
        entry_id = request.args.get("entry_id")

        path = "static/imgs/logo.png"

        return send_file(path, "image/png")

    @flask_app.route("/test", methods=["GET", "POST"])
    def test():
        import datetime

        return "Welcome! The time is {}".format(str(datetime.datetime.now()))

    @flask_app.route("/new_entry", methods=["GET", "POST"])
    def new_entry():
        from datetime import datetime

        timestamp = str(datetime.now().timestamp())

        coln = app.mongo_cx.entries_coln

        coln.insert_one({"name": "Hammer", "added_timestamp": timestamp})

        return "Welcome! The time is {}  {}".format(str(datetime.now()), timestamp)

    # @flask_app.before_request
    # def load_logged_in_user():
    #     g.user = session.get('user')
    #
    #     g.userinfo = g.user.get('userinfo') if g.user is not None else None
    #     g.user_sid = g.userinfo.get('sid') if g.userinfo is not None else None
    #     g.user_sub = g.userinfo.get('sub') if g.userinfo is not None else None
