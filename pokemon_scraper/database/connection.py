# connection.py
#
# MongoDB client for the Pokémon WebCrawler project.
# Loads configuration from a .env file using python-dotenv.
# Handles connection setup, collection access, and safe disconnection.

import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class MongoDBClient:
    def __init__(self, uri=None, db_name=None):
        self.uri = uri or os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.db_name = db_name or os.getenv("MONGO_DB_NAME", "pokemon_db")
        self.client = None
        self.db = None

    def connect(self):
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command("ping")  # Verifies connection
            self.db = self.client[self.db_name]
            logging.info(f"✅ Connected to MongoDB: {self.uri}")
            return self.db
        except ConnectionFailure as e:
            logging.error(f"❌ MongoDB connection failed: {e}")
            return None

    def get_collection(self, collection_name: str):
        if self.db is None:
            self.connect()
        return self.db[collection_name] if self.db is not None else None

    def close(self):
        if self.client:
            self.client.close()
            logging.info("🔌 MongoDB connection closed.")
