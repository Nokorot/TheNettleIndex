import os
from typing import Optional
from urllib.parse import urlparse

from pyimgur import Imgur

from src.nettle_app import NettleApp


class MyImgur(Imgur):

    def __init__(self, app: NettleApp):
        self.app = app

        imgur_secrets: Optional[dict] = app.config.secrets.get("Imgur")
        assert imgur_secrets is not None, "Failed to find Imgur secrets"

        super(MyImgur, self).__init__(self, imgur_secrets["CLIENT_ID"])
        self.client_secret = (imgur_secrets["CLIENT_SECRET"],)
        self.access_token = (imgur_secrets["ACCESS_TOKEN"],)
        self.refresh_token = (imgur_secrets["REFRESH_TOKEN"],)

    def parse_image_url(self, image_url: str) -> str:
        path = urlparse(image_url).path
        filename = os.path.basename(path)
        image_id, _ = os.path.splitext(filename)
        return image_id

    def delete_image(self, image_id: str):
        image = self.get_image(image_id)
        image.delete()
