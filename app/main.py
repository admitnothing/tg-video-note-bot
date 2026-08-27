import asyncio
import os

import httpx

from database import init_database
from handlers import handle_update
from telegram_api import get_updates


async def process_update(client, token, update):
    try:
        await handle_update(
            client,
            token,
            update
        )

    except Exception as error:
        print(
            f"Update {update.get('update_id')} failed: {error}",
            flush=True
        )


async def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    await init_database()

    offset = None
    tasks = set()

    timeout = httpx.Timeout(
        connect=10,
        read=40,
        write=10,
        pool=10
    )

    async with httpx.AsyncClient(timeout=timeout) as client:
        while True:
            try:
                data = await get_updates(
                    client,
                    token,
                    offset
                )

                if not data.get("ok"):
                    raise RuntimeError(
                        f"getUpdates failed: {data}"
                    )

                for update in data.get("result", []):
                    offset = update["update_id"] + 1

                    task = asyncio.create_task(
                        process_update(
                            client,
                            token,
                            update
                        )
                    )

                    tasks.add(task)
                    task.add_done_callback(tasks.discard)

            except Exception as error:
                print(
                    f"Polling error: {error}",
                    flush=True
                )

                await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())