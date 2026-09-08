import asyncio
import os
import uuid
import yt_dlp

from config import DOWNLOAD_DIR

YDL_SEARCH_OPTS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "ytsearch1",
    "skip_download": True,
}

YDL_DOWNLOAD_OPTS_TEMPLATE = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
}


class Track:
    def __init__(self, title: str, url: str, duration: int, filepath: str = None):
        self.title = title
        self.url = url
        self.duration = duration
        self.filepath = filepath


async def search(query: str) -> Track:
    """Search YouTube for a query (or accept a direct URL) and return metadata."""
    loop = asyncio.get_event_loop()

    def _search():
        with yt_dlp.YoutubeDL(YDL_SEARCH_OPTS) as ydl:
            info = ydl.extract_info(query, download=False)
            if "entries" in info:
                info = info["entries"][0]
            return info

    info = await loop.run_in_executor(None, _search)
    return Track(title=info.get("title", "Unknown"), url=info["webpage_url"], duration=info.get("duration", 0))


async def download(track: Track) -> Track:
    """Download the audio for a Track and set its local filepath."""
    loop = asyncio.get_event_loop()
    out_template = os.path.join(DOWNLOAD_DIR, f"{uuid.uuid4()}.%(ext)s")

    def _download():
        opts = dict(YDL_DOWNLOAD_OPTS_TEMPLATE)
        opts["outtmpl"] = out_template
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([track.url])
        # postprocessor converts to mp3
        base = out_template.rsplit(".", 1)[0]
        return base + ".mp3"

    filepath = await loop.run_in_executor(None, _download)
    track.filepath = filepath
    return track
