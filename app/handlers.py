from database import save_user, save_message
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
    document = message.get("document")

    if text is not None:
        message_type = "text"

    elif "video" in message:
        message_type = "video"

    elif (
        document is not None
        and document.get("mime_type", "").startswith("video/")
    ):
        message_type = "video"

    else:
        message_type = "other"

    await save_message(
        telegram_message_id=message["message_id"],
        user_id=user["id"],
        direction="incoming",
        message_type=message_type,
        text=text
    )
    
    if text == "/start":
        response = await send_message(
            client,
            token,
            chat_id,
            "Привет! Отправь мне видео до 60 секунд, "
            "и я превращу его в кружочек."
        )

        if response.get("ok"):
            sent_message = response["result"]

            await save_message(
                telegram_message_id=sent_message["message_id"],
                user_id=user["id"],
                direction="outgoing",
                message_type="text",
                text=sent_message.get("text")
            )

        return