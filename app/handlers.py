from database import save_user, save_message
from telegram_api import send_message, get_file


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
    video = message.get("video")

    if text is not None:
        message_type = "text"
        video_file = None

    elif video is not None:
        message_type = "video"
        video_file = video

    elif (
        document is not None
        and document.get("mime_type", "").startswith("video/")
    ):
        message_type = "video"
        video_file = document

    else:
        message_type = "other"
        video_file = None
        
    if video_file is not None:
        file_id = video_file["file_id"]
        file_data = await get_file(
            client,
            token,
            file_id
        )
        telegram_file_path = file_data["result"]["file_path"]
        print(telegram_file_path, flush=True) 
    
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