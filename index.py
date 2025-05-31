import os
import sys

from src import NettleApp

app = NettleApp()
flask_app = app.flask_app


# Ensure the cache dictionary exists
# if not os.path.exists('./cache'):
#     os.makedirs("./cache")

if __name__ == "__main__":
    port: int = app.config.get("DEBUG_PORT")

    flask_app.run(debug=True, port=port)
    flask_app.run(port=port)
