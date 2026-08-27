import httpx


API_BASE = "http://telegram-bot-api:8081"


async def get_updates(client, token, offset=None):
    url = f"{API_BASE}/bot{token}/getUpdates"

    params = {
        "timeout": 30
    }

    if offset is not None:
        params["offset"] = offset

    response = await client.get(url, params=params)
    response.raise_for_status()

    return response.json()


async def send_message(client, token, chat_id, text):
    url = f"{API_BASE}/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    response = await client.post(url, json=payload)
    response.raise_for_status()

    return response.json()


async def get_file(client, token, file_id):
    url = f"{API_BASE}/bot{token}/getFile"

    params = {
        "file_id": file_id
    }

    response = await client.get(url, params=params, timeout=120)
    
    response.raise_for_status()

    return response.json()


async def send_video_note(client, token, chat_id, file_path):
    url = f"{API_BASE}/bot{token}/sendVideoNote"

    with open(file_path, "rb") as video_file:
        files = {
            "video_note": (
                "video_note.mp4",
                video_file,
                "video/mp4"
            )
        }

        data = {
            "chat_id": str(chat_id)
        }

        response = await client.post(
            url,
            data=data,
            files=files
        )

    response.raise_for_status()

    return response.json()