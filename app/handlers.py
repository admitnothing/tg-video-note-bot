from pathlib import Path
from database import save_user, save_message, save_video, update_video
from telegram_api import send_message, get_file, send_video_note
from video import save_original, get_duration, convert_video

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
    
    await save_message(
        telegram_message_id=message["message_id"],
        user_id=user["id"],
        direction="incoming",
        message_type=message_type,
        text=text
    )
        
    if video is not None and video["duration"] > 60:
        response = await send_message(
            client,
            token,
            chat_id,
            "Видео слишком длинное. Пожалуйста, пришлите ролик до 60 секунд"
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
        
    if video_file is not None:
        file_id = video_file["file_id"]
        file_data = await get_file(
            client,
            token,
            file_id
        )
        telegram_file_path = file_data["result"]["file_path"]
        
        suffix = Path(telegram_file_path).suffix or ".mp4"

        file_name, original_path = await save_original(
            telegram_file_path,
            suffix
        )

        duration = await get_duration(original_path)
        video_id = await save_video(
            user_id=user["id"],
            telegram_file_id=file_id,
            duration=duration,
            original_path=original_path
        )
        
        if duration > 60:
            await update_video(
                video_id,
                status="rejected"
            )
            
            response = await send_message(
                client,
                token,
                chat_id,
                "Видео слишком длинное. Пожалуйста, пришлите ролик до 60 секунд"
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
        
        converted_name = f"{Path(file_name).stem}.mp4"
        converted_path = Path("/storage/converted") / converted_name
        await update_video(
            video_id,
            status="processing"
        )

        try:
            await convert_video(
                original_path,
                converted_path
            )

            response = await send_video_note(
                client,
                token,
                chat_id,
                converted_path
            )

            if response.get("ok"):
                sent_message = response["result"]

                await save_message(
                    telegram_message_id=sent_message["message_id"],
                    user_id=user["id"],
                    direction="outgoing",
                    message_type="video_note",
                    text=None
                )

                await update_video(
                    video_id,
                    status="completed",
                    converted_path=converted_path
                )

        except Exception as error:
            await update_video(
                video_id,
                status="failed"
            )

            print(
                f"Video {video_id} failed: {error}",
                flush=True
            )

            response = await send_message(
                client,
                token,
                chat_id,
                "Не удалось обработать видео. Попробуйте ещё раз."
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
    
    response = await send_message(
        client,
        token,
        chat_id,
        "Пожалуйста, отправьте видео до 60 секунд."
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