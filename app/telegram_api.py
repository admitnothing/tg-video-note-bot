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