import os
import sys
from typing import Optional

import pymongo
from pymongo.errors import ConfigurationError

from .nettle_app import NettleApp


class MongoConnection:
    def __init__(self, app: NettleApp):
        self.app = app
        self.URI = app.config.get("MONGODB_URI")
        self.DB = app.config.get("MONGODB_DB")

    def connect(self):

        try:
            self.client = pymongo.MongoClient(self.URI)
            self.mongodb = self.client[self.DB]
            self.app.logger.INFO("connected")
        except ConfigurationError:
            self.app.logger.ERROR(
                "An Invalid URI host error was received.\n"
                "Is your Atlas host name correct in your connection string?"
            )
            sys.exit(1)

        self.entries_coln = self.mongodb["entries"]
