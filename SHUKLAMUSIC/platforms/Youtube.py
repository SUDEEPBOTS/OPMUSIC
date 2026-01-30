import asyncio
import os
import re
import aiohttp
from typing import Union
import requests
# yt-dlp import removed completely
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch
from SHUKLAMUSIC.utils.database import is_on_off
from SHUKLAMUSIC.utils.formatters import time_to_seconds
import config
from config import API_URL, VIDEO_API_URL, API_KEY

# Aria2c Helper Function
async def download_with_aria2(url: str, file_path: str):
    if os.path.exists(file_path):
        return file_path
    
    # Ensure directory exists
    download_dir = os.path.dirname(file_path)
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    filename = os.path.basename(file_path)
    
    cmd = [
        "aria2c",
        "-x16", # 16 Connections
        "-s16", # Split 16
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
        print(f"Aria2 Error: {e}")
    return None

# Modified to use API + Aria2
async def download_song(link: str):
    video_id = link.split('v=')[-1].split('&')[0]
    download_folder = "downloads"
    file_path = f"{download_folder}/{video_id}.mp3"
    
    if os.path.exists(file_path):
        return file_path
        
    song_url = f"{API_URL}/song/{video_id}?api={API_KEY}"
    
    download_url = None
    async with aiohttp.ClientSession() as session:
        for attempt in range(5): # Reduced retries
            try:
                async with session.get(song_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        status = data.get("status", "").lower()
                        if status == "done":
                            download_url = data.get("link")
                            break
                        elif status == "downloading":
                            await asyncio.sleep(3)
            except:
                pass
    
    if download_url:
        # Using Aria2c instead of slow python write
        return await download_with_aria2(download_url, file_path)
    return None

# Modified to use API + Aria2
async def download_video(link: str):
    video_id = link.split('v=')[-1].split('&')[0]
    download_folder = "downloads"
    file_path = f"{download_folder}/{video_id}.mp4"
    
    if os.path.exists(file_path):
        return file_path
        
    video_url = f"{VIDEO_API_URL}/video/{video_id}?api={API_KEY}"
    
    download_url = None
    async with aiohttp.ClientSession() as session:
        for attempt in range(5):
            try:
                async with session.get(video_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        status = data.get("status", "").lower()
                        if status == "done":
                            download_url = data.get("link")
                            break
                        elif status == "downloading":
                            await asyncio.sleep(3)
            except:
                pass

    if download_url:
        return await download_with_aria2(download_url, file_path)
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

    # 🔥 REPLACED YT-DLP WITH API LOGIC
    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        # Extract ID
        try:
            vid_id = link.split('v=')[-1].split('&')[0]
        except:
            return 0, "Invalid Link"

        # Fetch Direct Link from API
        video_url = f"{VIDEO_API_URL}/video/{vid_id}?api={API_KEY}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(video_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "done":
                            return 1, data.get("link") # Return Direct URL
            except Exception as e:
                print(f"API Video Fetch Error: {e}")
        
        return 0, "Failed to fetch video url from API"

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        # Playlist usually requires yt-dlp to parse fast. 
        # Since we removed yt-dlp, we return empty or you need a playlist API.
        # Keeping it empty/safe to avoid errors.
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

    # Removed 'formats' function as it purely relied on yt-dlp

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

    # 🔥 MAIN DOWNLOADER REPLACED (API + ARIA2 ONLY)
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

        # Logic: Always use the helper functions which now use API+Aria2
        if video:
            downloaded_file = await download_video(link)
            direct = True # Since it's from API, we treat it as direct
        else:
            # Covers audio, songaudio, etc.
            downloaded_file = await download_song(link)
            direct = True

        if downloaded_file:
            return downloaded_file, direct
        else:
            # Final fallback if API completely fails
            return None, False
    
