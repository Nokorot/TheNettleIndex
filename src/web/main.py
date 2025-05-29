from flask import Flask


def route(app: Flask):

    @app.route("/")
    def home():
        return "Welcome to the web"
        # return render_template('home.html')

    @app.route("/test", methods=["GET", "POST"])
    def test():
        import datetime

        return "Welcome! The time is {}".format(str(datetime.datetime.now()))

    # @app.before_request
    # def load_logged_in_user():
    #     g.user = session.get('user')
    #
    #     g.userinfo = g.user.get('userinfo') if g.user is not None else None
    #     g.user_sid = g.userinfo.get('sid') if g.userinfo is not None else None
    #     g.user_sub = g.userinfo.get('sub') if g.userinfo is not None else None
