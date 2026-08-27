import os
from datetime import datetime, timezone

from pymongo import AsyncMongoClient


MONGO_URI = os.getenv("MONGO_URI")

client = AsyncMongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)

db = client["video_note_bot"]

users = db["users"]
messages = db["messages"]
videos = db["videos"]


async def init_database():
    await users.create_index(
        "telegram_id",
        unique=True
    )


async def save_user(telegram_id, username, first_name):
    now = datetime.now(timezone.utc)

    await users.update_one(
        {"telegram_id": telegram_id},
        {
            "$set": {
                "username": username,
                "first_name": first_name,
                "updated_at": now
            },
            "$setOnInsert": {
                "created_at": now
            }
        },
        upsert=True
    )