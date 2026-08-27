from database import save_user
from telegram_api import send_message


async def handle_update(client, token, update):
    message = update.get("message")

    if message is None:
        return

    user = message["from"]

    await save_user(
        telegram_id=user["id"],
        username=user.get("username"),
        first_name=user.get("first_name")
    )

    chat_id = message["chat"]["id"]
    text = message.get("text")

    if text == "/start":
        await send_message(
            client,
            token,
            chat_id,
            "Привет! Отправь мне видео до 60 секунд, "
            "и я превращу его в кружочек."
        )