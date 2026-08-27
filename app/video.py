import asyncio
import shutil
import uuid
from pathlib import Path


ORIGINALS_DIR = Path("/storage/originals")
CONVERTED_DIR = Path("/storage/converted")
SEMAPHORE = asyncio.Semaphore(2)


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


async def get_duration(file_path):
    process = await asyncio.create_subprocess_exec(
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        error = stderr.decode(errors="replace")
        raise RuntimeError(f"FFprobe failed:\n{error}")

    return float(stdout.decode().strip())


async def convert_video(input_path, output_path):
    async with SEMAPHORE:
        process = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-y",
            "-i", str(input_path),

            "-vf",
            (
                "crop='min(iw,ih)':'min(iw,ih)',"
                "scale='min(640,iw)':'min(640,ih)'"
            ),

            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",

            "-c:a", "aac",
            "-b:a", "128k",

            "-movflags", "+faststart",

            str(output_path),

            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            _, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=120
            )

        except TimeoutError:
            process.kill()
            await process.wait()
            raise RuntimeError("Video conversion timed out")

        if process.returncode != 0:
            error = stderr.decode(errors="replace")
            raise RuntimeError(
                f"FFmpeg conversion failed:\n{error}"
            )

    return output_path