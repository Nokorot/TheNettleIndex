import os
from datetime import datetime

from bson import ObjectId  # type: ignore
from flask import abort, redirect, render_template, request, url_for
from pymongo.database import Collection  # type: ignore
from werkzeug.utils import secure_filename

from src.nettle_app import NettleApp

ALLOWED_IMGAGE_EXTENSIONS = ["png", "jpg", "jpeg", "gif", "svg"]  # , "webp"


def route(app: NettleApp):
    flask_app = app.flask_app

    DB_ENTRY_VERSION = app.config["DB_ENTRY_VERSION"]

    assert app.mongo_cx.entries_coln is not None
    entries_coln: Collection = app.mongo_cx.entries_coln

    assert app.mongo_cx.tags_coln is not None
    tags_collection: Collection = app.mongo_cx.tags_coln


    ## Pages

    @flask_app.route("/new_entry")
    def new_entry():
        # Fetch all available tags for the dropdown
        tags = [tag.get("name") for tag in tags_collection.find()]
        return render_template("new_entry.html", app=app, existing_tags=tags)

    @flask_app.route("/entry/<entry_id>", methods=["GET", "POST"])
    def edit_entry(entry_id):
        entry = entries_coln.find_one({"_id": ObjectId(entry_id)})

        if not entry:
            abort(404)

        # Fetch all existing tags
        tags_collection = app.mongo_cx.tags_coln
        existing_tags = [tag.get("name") for tag in tags_collection.find()]

        # Render template with entry data and tags
        return render_template(
            "edit_entry.html",
            app=app,
            entry={
                "_id": entry_id,
                "name": entry.get("name"),
                "description": entry.get("description"),
                "owner": entry.get("owner"),
                "image_url": entry.get("icon_url"),
                "time_added": entry.get("added_timestamp"),
                "tags": entry.get("tags", []),
            },
            existing_tags=existing_tags,
        )

    ## Api

    @flask_app.route("/api/submit_entry", methods=["POST"])
    def api_submit_entry():
        selected_tags = request.form.getlist("tags")
        new_tags = request.form.get("new_tags", "").split(",")  # Get new tags as a comma-separated string

        # Combine existing and new tags
        all_tags = selected_tags + [tag.strip() for tag in new_tags if tag.strip()]

        data = {
            "version": DB_ENTRY_VERSION,
            "name": request.form["name"],
            "owner": request.form["owner"],
            "tags": all_tags,
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

        # Save the new entry to the database
        entries_coln.insert_one(data)

        # Add new tags to the tags collection if they don't exist
        for tag in all_tags:
            if not tags_collection.find_one({"name": tag}):
                tags_collection.insert_one({"name": tag})

        return "Entry successfully submitted", 204  # No Content

    @flask_app.route("/api/update_entry", methods=["POST"])
    def api_update_entry():
        entry_id = request.form["_id"]
        entry = entries_coln.find_one({"_id": ObjectId(entry_id)})
        if not entry:
            abort(404)

        # Get updated tags from the form
        selected_tags = request.form.getlist("tags")  # Tags from the 'added_tags' dropdown
        print("Selected tags:", selected_tags)

        # Update entry data
        data = {
            "name": request.form.get("name"),
            "description": request.form.get("description"),
            "tags": selected_tags,  # Update tags
        }

        # Handle image
        image = request.form.get("image")
        print("Image file:", image)
        while image is not None:
            icon_upload_path = upload_image(request.form.get("image"))

            print("Icon upload path:", icon_upload_path)
            if icon_upload_path is None:
                app.logger.WARNING("Warning: There was no image uploaded")
                break

            old_image_url = entry.get("icon_url")
            if old_image_url:
                print("Deleting old imgur image")
                old_image_id = app.imgur.parse_image_url(old_image_url)
                app.imgur.delete_image(old_image_id)

            name = data.get("name") or entry.get("name")
            print("Uploading new imgur image", icon_upload_path)
            imgur_image = app.imgur.upload_image(icon_upload_path, title=name)
            data["icon_url"] = imgur_image.link
            break



        # Update the entry in the database
        entries_coln.update_one({"_id": ObjectId(entry_id)}, {"$set": data})

        # Add new tags to the tags collection if they don't exist
        tags_collection = app.mongo_cx.tags_coln
        for tag in selected_tags:
            if not tags_collection.find_one({"name": tag}):
                tags_collection.insert_one({"name": tag})

        return "Entry successfully updated", 204  # No Content

    @flask_app.route("/api/delete_entry", methods=["POST"])
    def delete_entry():
        entry_id = request.form["_id"]
        entry = entries_coln.find_one({"_id": ObjectId(entry_id)})

        if not entry:
            abort(404)

        icon_url = entry.get("icon_url")
        if icon_url is not None:
            image_id = app.imgur.parse_image_url(icon_url)
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
