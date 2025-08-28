import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:4200").split(",")
    MONGO_URI = os.getenv(
        "MONGO_URI",
        "mongodb+srv://<username>:<password>@cluster0.mongodb.net/",
    )
    MONGO_DB_USERS = os.getenv("MONGO_DB_USERS", "flaskdb")
    MONGO_COLLECTION_USERS = os.getenv("MONGO_COLLECTION_USERS", "user")
    MONGO_DB_BOOKS = os.getenv("MONGO_DB_BOOKS", "mylibrary")
    MONGO_COLLECTION_BOOKS = os.getenv("MONGO_COLLECTION_BOOKS", "books")
