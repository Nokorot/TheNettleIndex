import sys
from typing import Optional

import pymongo
from pymongo.collation import Collation
from pymongo.database import Collection, Database
from pymongo.errors import ConfigurationError

from .nettle_app import NettleApp


class MongoConnection:
    def __init__(self, app: NettleApp):
        self.app = app
        self.secrets: Optional[dict] = app.config.secrets.get("MongoDB")
        if self.secrets is None:
            app.logger.ERROR("Missing MongoDB secrets")
            exit(1)
        self.uri: str = self.secrets.get("URI")
        self.db_name = self.secrets.get("db_name")

        self.client: Optional[pymongo.MongoClient] = None
        self.mongodb: Optional[Database] = None
        self.entries_coln: Optional[Collection] = None

    def connect(self):
        try:
            self.client = pymongo.MongoClient(self.uri)
            self.mongodb = self.client[self.db_name]
            self.app.logger.INFO("MongoDB connected")
        except ConfigurationError:
            self.app.logger.ERROR(
                "An Invalid URI host error was received.\n"
                "Is your Atlas host name correct in your connection string?"
            )
            sys.exit(1)

        self.entries_coln = self.mongodb["entries"]
