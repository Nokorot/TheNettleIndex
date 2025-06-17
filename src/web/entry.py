import os
from datetime import datetime

from bson import ObjectId  # type: ignore
from flask import abort, redirect, render_template, request, url_for
from pymongo.database import Collection  # type: ignore
from werkzeug.utils import secure_filename

from src.nettle_app import NettleApp

DB_ENTRY_VERSION = "0.2.0"
ALLOWED_IMGAGE_EXTENSIONS = ["png", "jpg", "jpeg", "gif", "svg"]  # , "webp"


def route(app: NettleApp):
    flask_app = app.flask_app

    assert app.mongo_cx.entries_coln is not None
    entries_coln: Collection = app.mongo_cx.entries_coln
    ## Pages

    @flask_app.route("/new_entry")
    def new_entry():
        return render_template("new_entry.html")

    @flask_app.route("/entry/<entry_id>", methods=["GET", "POST"])
    def entry_detail(entry_id):
        entry = entries_coln.find_one({"_id": ObjectId(entry_id)})

        if not entry:
            abort(404)

        # Render template with entry data
        return render_template(
            "entry_detail.html",
            entry={
                "_id": entry_id,
                "name": entry.get("name"),
                "description": entry.get("description"),
                "owner": entry.get("owner"),
                "image_url": entry.get("icon_url"),
                "time_added": entry.get("added_timestamp"),
            },
        )

    ## Api

    @flask_app.route("/api/submit_entry", methods=["POST"])
    def api_submit_entry():
        data = {
            "name": request.form["name"],
            "owner": request.form["owner"],
            "description": request.form["description"],
        }

        image = request.files.get("image")
        if image is None:
            app.logger.WARNING("Warning: There was no image uploaded")
        else:
            icon_upload_path = upload_image(image)

            imgur_image = app.imgur.upload_image(
                icon_upload_path, title=data.get("name")
            )
            data["icon_url"] = imgur_image.link

        restult = entries_coln.insert_one(data)
        _ = restult

        return "Entry successfully submitted", 204  # No Content

    @flask_app.route("/api/update_entry", methods=["POST"])
    def api_update_entry():
        entry_id = request.form["_id"]
        entry = entries_coln.find_one({"_id": ObjectId(entry_id)})
        if not entry:
            abort(404)

        data = {
            "name": request.form.get("name"),
            "description": request.form.get("description"),
        }

        # Handle form submission: update name, description, image
        image = request.files.get("image")
        if image is not None:
            icon_upload_path = upload_image(image)

            old_image_url = entry.get("icon_url")
            if old_image_url:
                print("Deleting old imgur image")
                app.imgur.delete_image(old_image_url)

            name = data.get("name") or entry.get("name")
            print("Uploading new imgur image", icon_upload_path)
            imgur_image = app.imgur.upload_image(icon_upload_path, title=name)
            data["icon_url"] = imgur_image.link

        entries_coln.update_one(
            {"_id": entry.get("_id")},
            {"$set": data},
        )

        return redirect(url_for("entry_detail", entry_id=entry_id))

    @flask_app.route("/api/delete_entry", methods=["POST"])
    def delete_entry():
        entry_id = request.form["_id"]
        entry = entries_coln.find_one({"_id": ObjectId(entry_id)})

        if not entry:
            abort(404)

        image_url = entry.get("icon_url")
        image_id = app.imgur.parse_image_url(image_url)
        app.imgur.delete_image(image_id)

        entries_coln.delete_one({"_id": ObjectId(entry_id)})
        return redirect(url_for("home"))

    # Helper functions

    UPLOAD_FOLDER = app.config["FOLDERS"]["UPLOAD"]

    def upload_file(file, ALLOWED_EXTENSIONS=None):
        extension = os.path.splitext(file.filename)[1]

        if (
            ALLOWED_EXTENSIONS is not None
            and len(extension) < 1
            and extension[1:] not in ALLOWED_EXTENSIONS
        ):
            app.logger.WARNING(
                f"Warning: The uploaded image has an invalid extension [{extension}]"
            )
            return None

        # Make filename safe and unique
        time = str(datetime.now().timestamp())
        upload_filename = f"{time}_{secure_filename(file.filename)}"
        upload_path = os.path.join(UPLOAD_FOLDER, upload_filename)
        file.save(upload_path)

        app.logger.INFO(f"File '{file.filename}' uploaded to '{upload_path}'")
        return upload_path

    def upload_image(file):
        return upload_file(file, ALLOWED_IMGAGE_EXTENSIONS)
