import asyncio
import shutil
import uuid
from pathlib import Path


ORIGINALS_DIR = Path("/storage/originals")
CONVERTED_DIR = Path("/storage/converted")


async def save_original(source_path, suffix):
    source_path = Path(source_path)

    if not source_path.is_file():
        raise FileNotFoundError(source_path)

    file_name = f"{uuid.uuid4()}{suffix}"
    destination = ORIGINALS_DIR / file_name

    await asyncio.to_thread(
        shutil.copy2,
        source_path,
        destination
    )

    return file_name, destination