import os
import sys
from datetime import datetime
from typing import Optional

from flask import make_response, redirect, render_template, request, send_file, url_for
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
    ICON_FOLDER = FOLDERS["ICON"]
    UPLOAD_FOLDER = FOLDERS["UPLOAD"]

    def imgur_upload_image(str_id: str, title: str) -> Optional[str]:
        logger.INFO(f"Uploading image for {str_id}")

        image_path = os.path.join(ICON_FOLDER, f"{str_id}.img")
        if not os.path.exists(image_path):
            logger.INFO(f"Image path {image_path} does not exist")

            return None

        imgur_image = app.imgur.upload_image(image_path, title=title)
        if imgur_image is None:
            logger.INFO("Failed to upload image")
            return None

        image_url = imgur_image.link
        logger.INFO(f"Image '{image_path}' uploaded to '{image_url}'")

        return image_url

    @flask_app.route("/")
    def home():
        qfilter = {}
        entries = []

        for c in coln.find(qfilter):
            _id = c.get("_id")
            str_id = str(_id)

            version = c.get("version")

            if version is None:
                new_url = imgur_upload_image(str_id, c.get("name") or "")

                if new_url is not None:
                    coln.update_one(
                        {"_id": _id},
                        {"$set": {"icon_url": new_url, "version": DB_ENTRY_VERSION}},
                    )

            image_url = c.get("icon_url")

            entries.append(
                {
                    "id": str_id,
                    "name": c.get("name"),
                    "description": c.get("description"),
                    "owner": c.get("owner"),
                    "image_url": image_url,
                    "time_added": c.get("added_timestamp"),
                }
            )

        return render_template("main.html", entries=entries)

    @flask_app.route("/media/entry-icon", methods=["GET"])
    def entry_icon():
        entry_id = request.args.get("entry_id")

        filename = f"{entry_id}.img"

        file_path = os.path.join(ICON_FOLDER, filename)

        if not os.path.exists(file_path):
            return "File not found", 404

        # Get last modified time of the file
        last_modified = datetime.fromtimestamp(os.path.getmtime(file_path))

        # Compare with client's If-Modified-Since header
        if_modified_since = request.headers.get("If-Modified-Since")
        if if_modified_since:
            try:
                since_time = datetime.strptime(
                    if_modified_since, "%a, %d %b %Y %H:%M:%S GMT"
                )
                if since_time >= last_modified:
                    return "", 304
            except ValueError:
                pass  # if header is malformed, ignore it

        # TODO Fix the mimetype
        response = make_response(send_file(file_path, mimetype="image/jpeg"))
        response.headers["Last-Modified"] = http_date(os.path.getmtime(file_path))
        response.headers["Cache-Control"] = "public, max-age=86400"

        return response

    @flask_app.route("/new_entry")
    def new_entry():
        return render_template("new_entry.html")

    @flask_app.route("/submit_entry", methods=["POST"])
    def submit_entry():
        entry = {}
        entry["version"] = DB_ENTRY_VERSION

        time = entry["timestamp"] = str(datetime.now().timestamp())
        entry["name"] = request.form.get("name")
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
            assert file.filename is not None

            # Make filename safe and unique
            image_filename = f"{time}_{secure_filename(file.filename)}"
            upload_path = os.path.join(UPLOAD_FOLDER, image_filename)

            print(f"File '{file.filename}' uploaded to '{upload_path}'")

            file.save(upload_path)

            # Maybe on a different thread :
            # TODO: Hash the file and downsize if needed
            #    (downsizing could also be done client-side)

            # TODO: app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB limit

            imgur_image = app.imgur.upload_image(upload_path, title=entry["name"])
            entry["icon_url"] = imgur_image.link

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
