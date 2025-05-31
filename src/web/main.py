from .. import NettleApp


def route(app: NettleApp):
    flask_app = app.flask_app

    coln = app.mongo_cx.entries_coln

    @flask_app.route("/")
    def home():
        qfilter = {}

        reply = "<html>"
        for c in coln.find(qfilter):
            name = c.get("name")

            if name is None:
                continue
            reply = "<tr>Name: %s</tr>" % name

        reply += "</html>"
        return reply
        # return render_template('home.html')

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
