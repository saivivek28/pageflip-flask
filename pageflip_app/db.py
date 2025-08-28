from pymongo import MongoClient
from .config import Config

_client = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(Config().MONGO_URI)
    return _client


def get_collections():
    client = get_client()
    users_col = client[Config().MONGO_DB_USERS][Config().MONGO_COLLECTION_USERS]
    books_col = client[Config().MONGO_DB_BOOKS][Config().MONGO_COLLECTION_BOOKS]
    return users_col, books_col
