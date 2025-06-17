import os
from typing import Optional
from urllib.parse import urlparse

from pyimgur import Image, Imgur  # type: ignore

from src.nettle_app import NettleApp


def imgur_parse_image_url(image_url: str) -> str:
    path = urlparse(image_url).path
    filename = os.path.basename(path)
    image_id, _ = os.path.splitext(filename)
    return image_id


class MyImgur:

    def __init__(self, app: NettleApp):
        self.app = app

        imgur_secrets: Optional[dict] = app.config.secrets.get("Imgur")
        assert imgur_secrets is not None, "Failed to find Imgur secrets"

        self.imgur = Imgur(
            client_id=imgur_secrets["CLIENT_ID"],
            client_secret=imgur_secrets["CLIENT_SECRET"],
            access_token=imgur_secrets["ACCESS_TOKEN"],
            refresh_token=imgur_secrets["REFRESH_TOKEN"],
        )

    def parse_image_url(self, image_url: str) -> str:
        return imgur_parse_image_url(image_url)

    def delete_image(self, image_id: str):
        image = self.imgur.get_image(image_id)
        image.delete()

    def upload_image(
        self, path=None, url=None, title=None, description=None, album=None
    ) -> Image:
        return self.imgur.upload_image(path, url, title, description, album)
