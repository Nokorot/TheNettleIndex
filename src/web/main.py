import sys

from datetime import datetime
from flask import render_template, request, redirect  # type: ignore

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
        selected_tags = request.args.get("tags")  # Tags selected for filtering
        page = int(request.args.get("page", 1))  # Default to page 1
        entries_per_page = app.config.get("ENTRIES_PER_PAGE", 10)  # Default to 10 if not set in config

        selected_tags = selected_tags.split(",") if selected_tags else []

        qfilter = {}
        if selected_tags and len(selected_tags) > 0:
            qfilter["tags"] = {"$all": selected_tags}  # Match entries containing all selected tags


        print(f"Query filter: {qfilter}")

        entries = []
        for c in coln.find(qfilter):
            entry = {
                "id": str(c.get("_id")),
                "name": c.get("name"),
                "description": c.get("description"),
                "owner": c.get("owner"),
                "image_url": c.get("icon_url"),
                "time_added": c.get("added_timestamp"),
                "tags": c.get("tags", []),
            }

            if search_query and search_query not in entry["name"].lower() and search_query not in entry["description"].lower():
                continue

            entries.append(entry)

        # Pagination logic
        total_entries = len(entries)
        start = (page - 1) * entries_per_page
        end = start + entries_per_page
        paginated_entries = entries[start:end]

        # Fetch all tags for the filter dropdown
        tags_collection = app.mongo_cx.tags_coln
        all_tags = [tag.get("name") for tag in tags_collection.find()]

        
        return render_template(
            "main.html",
            entries=paginated_entries,
            page=page,
            total_pages=(total_entries + entries_per_page - 1) // entries_per_page,
            all_tags=all_tags,
            selected_tags=selected_tags,
        )

    @flask_app.route("/test", methods=["GET", "POST"])
    def test():
        return "Welcome! The time is {}".format(str(datetime.now()))

    @flask_app.route("/tags", methods=["GET"])
    def get_tags():
        tags_collection = app.mongo_cx.tags_coln  # Ensure you have a tags collection
        if tags_collection is None:
            app.logger.ERROR("MongoDB tags collection is None")
            sys.exit(1)

        tags = [tag.get("name") for tag in tags_collection.find()]
        return {"tags": tags}

    # @flask_app.before_request
    # def load_logged_in_user():
    #     g.user = session.get('user')
    #
    #     g.userinfo = g.user.get('userinfo') if g.user is not None else None
    #     g.user_sid = g.userinfo.get('sid') if g.userinfo is not None else None
    #     g.user_sub = g.userinfo.get('sub') if g.userinfo is not None else None
