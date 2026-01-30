import asyncio
import os
import re
import aiohttp
from typing import Union
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch
from SHUKLAMUSIC.utils.database import is_on_off
from SHUKLAMUSIC.utils.formatters import time_to_seconds
from config import API_URL, API_KEY

# 🔥 1. ARIA2C DOWNLOADER HELPER
async def download_with_aria2(url: str, file_path: str):
    if os.path.exists(file_path):
        return file_path
    
    download_dir = os.path.dirname(file_path)
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    filename = os.path.basename(file_path)
    
    # Fast Download Command
    cmd = [
        "aria2c",
        "-x16", # 16 Connections
        "-s16", # Split into 16 parts
        "-d", download_dir,
        "-o", filename,
        url
    ]
    
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if os.path.exists(file_path):
            return file_path
    except Exception as e:
        print(f"❌ Aria2 Error: {e}")
    return None

# 🔥 2. UNIVERSAL API FETCHER (Based on your Curl)
async def get_api_link(query: str):
    # Ensure URL doesn't have double slashes
    base_url = API_URL.rstrip("/")
    url = f"{base_url}/getvideo"
    
    params = {
        "query": query,
        "key": API_KEY
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params, timeout=20) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Check if 'link' exists in response
                    if "link" in data:
                        return data["link"]
                    # Fallback check
                    if data.get("status") == 200 and "link" in data:
                        return data["link"]
        except Exception as e:
            print(f"⚠️ API Fetch Error: {e}")
    return None

# 🔥 3. DOWNLOAD LOGIC (Uses /getvideo for everything)
async def download_media(link: str, is_video: bool = False):
    try:
        # Extract ID or use Full Link as Query
        if "v=" in link:
            query = link.split('v=')[-1].split('&')[0]
        elif "youtu.be" in link:
            query = link.split("/")[-1].split("?")[0]
        else:
            query = link 

        # 1. Get Direct Link from API
        direct_url = await get_api_link(query)
        
        if not direct_url:
            print("❌ API did not return a link.")
            return None

        # 2. Determine Filename & Extension
        # API mostly returns .mp4 (from Catbox), even for songs
        ext = direct_url.split(".")[-1]
        if len(ext) > 4: # Safety check if no extension
            ext = "mp4"
            
        download_folder = "downloads"
        filename = f"{query}.{ext}"
        file_path = os.path.join(download_folder, filename)
        
        # 3. Download via Aria2
        return await download_with_aria2(direct_url, file_path)

    except Exception as e:
        print(f"Download Media Error: {e}")
    return None


async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        else:
            return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return text[offset : offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            if str(duration_min) == "None":
                duration_sec = 0
            else:
                duration_sec = int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
        return title

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            duration = result["duration"]
        return duration

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        return thumbnail

    # 🔥 REPLACED WITH API FETCH
    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        # Reuse download_media (It handles logic internally)
        file_path = await download_media(link, is_video=True)
        if file_path:
            return 1, file_path

        return 0, "Failed to fetch video"

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        return []

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    # 🔥 MAIN DOWNLOADER (Uses getvideo API + Aria2)
    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        
        if videoid:
            link = self.base + link

        # Calls the centralized download_media function
        # Since API returns a file (likely MP4), we just download it.
        # PyTgCalls will play the audio from the MP4 automatically if audio is requested.
        
        downloaded_file = await download_media(link, is_video=bool(video))
            
        if downloaded_file:
            return downloaded_file, True
        else:
            return None, False
        
