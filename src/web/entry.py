from flask import request

from src.nettle_app import NettleApp


class EntryManager:

    def __init__(self, app: NettleApp):
        self.app = app

    def new_entry(self, entry: dict):
        print("New Entry: ", entry)

        # upload_path = None
        # if file is None:
        #     logger.WARNING("Warning: There was no image uploaded")
        # elif not allowed_file(file.filename):
        #     assert file.filename is not None
        #     extension = os.path.splitext(file.filename)[1][1:]
        #
        #     logger.WARNING(
        #         f"Warning: The uploaded image has an invalid extension [{extension}]"
        #     )
        # else:
        #     entry["icon_url"] = image_upload_image(file, title=entry["name"])
        #
        # restult = coln.insert_one(entry)
        # _ = restult


def route(app: NettleApp):
    flask_app = app.flask_app

    manager = EntryManager(app)

    @flask_app.route("/api/submit_entry", methods=["GET", "POST"])
    def api_submit_entry():
        print("Api Submit")

        if request.method == "GET":
            return "Hello"

        image = request.files.get("image")
        img_data = image.read() if image else None
        filename = image.filename if image else None

        entry_data = {
            "name": request.form["name"],
            "owner": request.form["owner"],
            "description": request.form["description"],
            "icon_data": img_data,
            "icon_filename": filename,
        }

        print("Entry Data", entry_data)

        # manager.new_entry(entry_data)

        return "Entry successfully submitted", 204  # No Content
