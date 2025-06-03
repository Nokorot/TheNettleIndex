import logging
import os

from src import NettleApp

app = NettleApp("config.toml", ".secrets.toml")
flask_app = app.flask_app


## Ensure that all the necessary folders are available
for name, path in app.config.get("FOLDERS").items():
    os.makedirs(path, exist_ok=True)


## Suppress image requests
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
