import asyncio
import os

import httpx

from database import init_database
from telegram_api import get_updates, send_message
from handlers import handle_update


async def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    await init_database()

    offset = None

    timeout = httpx.Timeout(
        connect=10,
        read=40,
        write=10,
        pool=10
    )

    async with httpx.AsyncClient(timeout=timeout) as client:
        while True:
            data = await get_updates(
                client,
                token,
                offset
            )

            for update in data["result"]:
                offset = update["update_id"] + 1

                await handle_update(
                    client,
                    token,
                    update
                )

if __name__ == "__main__":
    asyncio.run(main())