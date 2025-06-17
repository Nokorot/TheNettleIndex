import sys

from flask import render_template, request  # type: ignore

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
        search_query = request.args.get("search", "").lower()
        page = int(request.args.get("page", 1))  # Default to page 1
        entries_per_page = app.config.get("ENTRIES_PER_PAGE", 10)  # Default to 10 if not set in config

        qfilter = {}
        entries = []

        for c in coln.find(qfilter):
            _id = c.get("_id")
            str_id = str(_id)

            version = c.get("version")
            _ = version

            entry = {
                "id": str_id,
                "name": c.get("name"),
                "description": c.get("description"),
                "owner": c.get("owner"),
                "image_url": c.get("icon_url"),
                "time_added": c.get("added_timestamp"),
            }

            # Filter entries based on the search query
            if search_query and search_query not in entry["name"].lower() and search_query not in entry["description"].lower():
                continue

            entries.append(entry)

        # Pagination logic
        total_entries = len(entries)
        start = (page - 1) * entries_per_page
        end = start + entries_per_page
        paginated_entries = entries[start:end]

        return render_template(
            "main.html",
            entries=paginated_entries,
            page=page,
            total_pages=(total_entries + entries_per_page - 1) // entries_per_page,
        )

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
