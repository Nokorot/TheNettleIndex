import os
import sys

from src import NettleApp

app = NettleApp()
flask_app = app.flask_app


# Ensure the cache dictionary exists
# if not os.path.exists('./cache'):
#     os.makedirs("./cache")


UPLOAD_FOLDER = os.path.join(flask_app.root_path, "media", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ICON_FOLDER = os.path.join(flask_app.root_path, "media", "entry_icons")
os.makedirs(ICON_FOLDER, exist_ok=True)

app.config.UPLOAD_FOLDER = UPLOAD_FOLDER
app.config.ICON_FOLDER = ICON_FOLDER

import logging


class SuppressMedia304(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        return not ("/media/entry-icon" in msg and ('"304' in msg))


# Apply to Werkzeug logger
log = logging.getLogger("werkzeug")
log.addFilter(SuppressMedia304())

if __name__ == "__main__":
    port: int = app.config.get("DEBUG_PORT")

    flask_app.run(debug=True, port=port)
    flask_app.run(port=port)
