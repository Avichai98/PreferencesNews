from pymongo import MongoClient
import os


class MongoDB:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
        self.db_name = os.getenv("MONGO_DB_NAME", "app")
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.db_name]

    def get_collection(self, collection_name):
        return self.db[collection_name]


mongo = MongoDB()
