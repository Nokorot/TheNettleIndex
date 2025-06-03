import os
import shutil
import sys
from datetime import datetime, timedelta

from flask import make_response, redirect, render_template, request, send_file, url_for
from werkzeug.http import http_date
from werkzeug.utils import secure_filename

from .. import NettleApp

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "svg"}


def allowed_file(filename):
    basename, extension = os.path.splitext(filename)

    print(filename, extension)

    return len(extension) > 0 and extension[1:] in ALLOWED_EXTENSIONS


def route(app: NettleApp):
    flask_app = app.flask_app

    coln = app.mongo_cx.entries_coln
    if coln is None:
        app.logger.ERROR("MongoDB collection is None")
        sys.exit(1)

    FOLDERS: dict = app.config["FOLDERS"]
    ICON_FOLDER = FOLDERS["ICON"]
    UPLOAD_FOLDER = FOLDERS["UPLOAD"]

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

        for i in range(100):
            id = i + 1
            entries.append(
                {
                    "id": id,
                    "name": "Object nr. %d" % id,
                    "description": f"This is the {id}'th generated example entry",
                    "owner": "Name nr. %s" % id,
                    "image_url": url_for("entry_icon", entry_id=id),
                    "time_added": (
                        datetime.now() - timedelta(hours=i * 10)
                    ).timestamp(),
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
        last_modified = datetime.utcfromtimestamp(os.path.getmtime(file_path))

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
        time = entry["timestamp"] = str(datetime.now().timestamp())
        entry["name"] = request.form.get("name")
        entry["description"] = request.form.get("description")
        entry["owner"] = request.form.get("owner")
        file = request.files.get("image")

        upload_path = None
        if file and allowed_file(file.filename):
            # Make filename safe and unique
            image_filename = f"{time}_{secure_filename(file.filename)}"
            upload_path = os.path.join(UPLOAD_FOLDER, image_filename)

            print(f"File '{file.filename}' uploaded to '{upload_path}'")

            file.save(upload_path)

        restult = coln.insert_one(entry)
        entry_id = str(restult.inserted_id)
        print("Id:" + entry_id)

        if upload_path:
            filename = f"{entry_id}.img"
            image_path = os.path.join(ICON_FOLDER, filename)

            print(f"'{upload_path}' moved to 'image_path'")
            shutil.move(upload_path, image_path)

            # Maybe on a different thread :
            ## TODO: Hash the file and downsize if needed
            #    (downsizing could also be done client-side)

            ##  TODO: app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB limit

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
