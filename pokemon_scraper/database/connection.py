from pymongo import MongoClient


def connect_to_mongodb(URI: str = "mongodb://localhost:27017/"):
    try:
        return MongoClient(URI)
    except Exception as e:
        print(f"Connection Error {e}")
        return None
