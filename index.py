import os
import sys

from flask import Flask

from src.config import Config, construct_config
from src.web import construct_app

config: Config = construct_config()
app: Flask = construct_app(config)


# Ensure the cache dictionary exists
# if not os.path.exists('./cache'):
#     os.makedirs("./cache")

if __name__ == "__main__":
    port: int = config.get("DEBUG_PORT")

    app.run(debug=True, port=port)
    app.run(port=port)
