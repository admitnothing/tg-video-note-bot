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


async def save_message(
    telegram_message_id,
    user_id,
    direction,
    message_type,
    text=None
):
    await messages.insert_one({
        "telegram_message_id": telegram_message_id,
        "user_id": user_id,
        "direction": direction,
        "type": message_type,
        "text": text,
        "created_at": datetime.now(timezone.utc)
    })
    
    
async def save_video(
    user_id,
    telegram_file_id,
    duration,
    original_path,
    converted_path=None,
    status="received"
):
    now = datetime.now(timezone.utc)

    result = await videos.insert_one({
        "user_id": user_id,
        "telegram_file_id": telegram_file_id,
        "duration": duration,
        "original_path": str(original_path),
        "converted_path": str(converted_path) if converted_path else None,
        "status": status,
        "created_at": now,
        "updated_at": now
    })

    return result.inserted_id 


async def update_video(
    video_id,
    *,
    status=None,
    converted_path=None
):
    updates = {
        "updated_at": datetime.now(timezone.utc)
    }

    if status is not None:
        updates["status"] = status

    if converted_path is not None:
        updates["converted_path"] = str(converted_path)

    await videos.update_one(
        {"_id": video_id},
        {"$set": updates}
    )   