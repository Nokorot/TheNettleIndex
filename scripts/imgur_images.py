import os
import sys
from typing import Optional

import pyimgur
import pymongo
from pymongo.auth import ConfigurationError

sys.path.append(os.path.curdir)

from src.logging import LoggerContext

logger = LoggerContext("")

ICON_FOLDER = "./media/entry_icons"


def read_toml(fname):
    import pytoml

    with open(fname, "rb") as fin:
        try:
            return pytoml.load(fin)
        except Exception as e:
            print("Toml Error: ", e)
            exit(1)


app_secrets = read_toml(".secrets.toml")

imgur_secrets: Optional[dict] = app_secrets.get("Imgur")
assert imgur_secrets is not None, "Failed to find Imgur secrets"

imgur = pyimgur.Imgur(
    imgur_secrets["CLIENT_ID"],
    imgur_secrets["CLIENT_SECRET"],
    access_token=imgur_secrets["ACCESS_TOKEN"],
    refresh_token=imgur_secrets["REFRESH_TOKEN"],
)


def imgur_upload_image(image_path: str, title: str) -> Optional[str]:

    logger.INFO(f"Uploading image {image_path}")

    if not os.path.exists(image_path):
        logger.INFO(f"Image path {image_path} does not exist")
        return None

    from PIL import Image

    with open(image_path, "rb") as fp:
        im = Image.open(fp)
        im.thumbnail((1024, 1024))

        out_path = image_path + "_thumb.png"
        im.save(out_path)

        image_path = out_path

    imgur_image = imgur.upload_image(image_path, title=title)
    if imgur_image is None:
        logger.INFO("Failed to upload image")
        return None

    image_url = imgur_image.link
    logger.INFO(f"Image '{image_path}' uploaded to '{image_url}'")

    return image_url


def _unused_():
    mdb_secrets: Optional[dict] = app_secrets.get("MongoDB")
    if mdb_secrets is None:
        logger.ERROR("Missing MongoDB secrets")
        exit(1)
    uri: str = mdb_secrets.get("URI")
    db_name = mdb_secrets.get("db_name")

    try:
        client = pymongo.MongoClient(uri)
        mongodb = client[db_name]
        logger.INFO("MongoDB connected")
    except ConfigurationError:
        logger.ERROR(
            "An Invalid URI host error was received.\n"
            "Is your Atlas host name correct in your connection string?"
        )
        exit(1)

    entries_coln = mongodb["entries"]

    DB_ENTRY_VERSION = "0.2.0"

    qfilter = {}

    for c in entries_coln.find(qfilter):
        _id = c.get("_id")
        str_id = str(_id)

        version = c.get("version")

        print(_id, version)

        if version is None:

            try:

                new_url = imgur_upload_image(str_id, c.get("name") or "")

                if new_url is not None:
                    entries_coln.update_one(
                        {"_id": _id},
                        {"$set": {"icon_url": new_url, "version": DB_ENTRY_VERSION}},
                    )
            except Exception:
                pass


url = imgur_upload_image("media/example.png", "Example Img")
print(url)
