import os
import sys
from datetime import datetime
from typing import Optional

from bson import ObjectId
from flask import (
    abort,
    make_response,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from werkzeug.datastructures import FileStorage
from werkzeug.http import http_date
from werkzeug.utils import secure_filename

from .. import NettleApp

ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "gif", "svg"]  # , "webp"
DB_ENTRY_VERSION = "0.2.0"


def allowed_file(filename):
    extension = os.path.splitext(filename)[1]
    return len(extension) > 0 and extension[1:] in ALLOWED_EXTENSIONS


def route(app: NettleApp):
    flask_app = app.flask_app
    logger = app.logger.sub_contex("web")

    coln = app.mongo_cx.entries_coln
    if coln is None:
        app.logger.ERROR("MongoDB collection is None")
        sys.exit(1)

    FOLDERS: dict = app.config["FOLDERS"]
    UPLOAD_FOLDER = FOLDERS["UPLOAD"]

    def imgur_delete_image(image_url):
        pass

    def image_upload_image(file, title=None):
        assert file is not None and file.filename is not None

        time = str(datetime.now().timestamp())

        # Make filename safe and unique
        image_filename = f"{time}_{secure_filename(file.filename)}"
        upload_path = os.path.join(UPLOAD_FOLDER, image_filename)

        print(f"File '{file.filename}' uploaded to '{upload_path}'")

        file.save(upload_path)

        # Maybe on a different thread :
        # TODO: Hash the file and downsize if needed
        #    (downsizing could also be done client-side)

        # TODO: app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB limit

        imgur_image = app.imgur.upload_image(upload_path, title=title)
        return imgur_image.link

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

    @flask_app.route("/entry/<entry_id>", methods=["GET", "POST"])
    def entry_detail(entry_id):
        entry = coln.find_one({"_id": ObjectId(entry_id)})

        if not entry:
            abort(404)

        if request.method == "POST":

            # Handle form submission: update name, description, image
            name = request.form.get("name")
            description = request.form.get("description")
            file = request.files.get("image")

            update_data = {"name": name, "description": description}

            if file and file.filename:
                # Upload to Imgur and update image_url
                image_url = image_upload_image(file, title=name)  # you'd implement this
                update_data["icon_url"] = image_url

            coln.update_one({"_id": ObjectId(entry_id)}, {"$set": update_data})
            return redirect(url_for("entry_detail", entry_id=entry_id))

        # Render template with entry data
        return render_template(
            "entry_detail.html",
            entry={
                "id": entry_id,
                "name": entry.get("name"),
                "description": entry.get("description"),
                "owner": entry.get("owner"),
                "image_url": entry.get("icon_url"),
                "time_added": entry.get("added_timestamp"),
            },
        )

    @flask_app.route("/entry/<entry_id>/delete", methods=["POST"])
    def delete_entry(entry_id):
        entry = coln.find_one({"_id": ObjectId(entry_id)})

        if not entry:
            abort(404)

        image_url = entry.get("icon_url")
        imgur_delete_image(image_url)

        coln.delete_one({"_id": ObjectId(entry_id)})
        return redirect(url_for("home"))

    @flask_app.route("/new_entry")
    def new_entry():
        return render_template("new_entry.html")

    @flask_app.route("/submit_entry", methods=["POST"])
    def submit_entry():
        entry = {}
        entry["version"] = DB_ENTRY_VERSION

        entry["timestamp"] = str(datetime.now().timestamp())
        name = entry["name"] = request.form.get("name")
        entry["description"] = request.form.get("description")
        entry["owner"] = request.form.get("owner")
        file: Optional[FileStorage] = request.files.get("image")

        upload_path = None
        if file is None:
            logger.WARNING("Warning: There was no image uploaded")
        elif not allowed_file(file.filename):
            assert file.filename is not None
            extension = os.path.splitext(file.filename)[1][1:]

            logger.WARNING(
                f"Warning: The uploaded image has an invalid extension [{extension}]"
            )
        else:
            entry["icon_url"] = image_upload_image(file, title=name)

        restult = coln.insert_one(entry)
        _ = restult

        return redirect(url_for("home"))

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
