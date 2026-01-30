import re
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

# Load environment variables
load_dotenv()

# Required credentials
API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
BOT_TOKEN = getenv("BOT_TOKEN")

# Bot and owner info
OWNER_USERNAME = getenv("OWNER_USERNAME", "HEHE_STALKER")
BOT_USERNAME = getenv("BOT_USERNAME", "tidalxmusicbot")
BOT_NAME = getenv("BOT_NAME", "TIDAL")
ASSUSERNAME = getenv("ASSUSERNAME", "THEDRXNET")

# MongoDB
MONGO_DB_URI = getenv("MONGO_DB_URI", None)
MONGO_DB_URL = getenv("MONGO_DB_URL", None)

# -----------------------------
# YouTube API configuration
API_URL = getenv("API_URL", 'https://fastapi2-wdtl.onrender.com') #youtube song url
API_KEY = getenv("API_KEY", None)

# Limits and IDs
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 17000))
LOGGER_ID = int(getenv("LOGGER_ID", -1002329141957))
OWNER_ID = int(getenv("OWNER_ID", 7659846392))

# Heroku
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

# Git
UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/shoaib910385/MyTidalMusic")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv("GIT_TOKEN", None)

# Support
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/thedrxnet")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/drx_supportchat")

# Assistant settings
AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", "True")
AUTO_LEAVE_ASSISTANT_TIME = int(getenv("ASSISTANT_LEAVE_TIME", "9000"))


# Server limits and configurations - These can be set based on your server configurations
SERVER_PLAYLIST_LIMIT = int(getenv("SERVER_PLAYLIST_LIMIT", "3000"))
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", "2500"))
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION", "9999999"))
SONG_DOWNLOAD_DURATION_LIMIT = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "9999999"))

# Spotify
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "1c21247d714244ddbb09925dac565aed")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "709e1a2969664491b58200860623ef19")

# Playlist limit
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))

# Telegram file limits
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "5242880000"))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "5242880000"))

# Session strings
STRING1 = getenv("STRING_SESSION", None)
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)
STRING6 = getenv("STRING_SESSION6", None)
STRING7 = getenv("STRING_SESSION7", None)

# Miscellaneous
BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

# Image URLs
START_IMG_URL = getenv("START_IMG_URL", "https://files.catbox.moe/wifnjm.jpg")
PING_IMG_URL = getenv("PING_IMG_URL", "https://files.catbox.moe/wifnjm.jpg")
PLAYLIST_IMG_URL = "https://telegra.ph/file/d723f4c80da157fca1678.jpg"
STATS_IMG_URL = "https://files.catbox.moe/wifnjm.jpg"
TELEGRAM_AUDIO_URL = "https://files.catbox.moe/2vq8oz.jpg"
TELEGRAM_VIDEO_URL = "https://files.catbox.moe/2vq8oz.jpg"
STREAM_IMG_URL = "https://files.catbox.moe/2vq8oz.jpg"
SOUNCLOUD_IMG_URL = "https://files.catbox.moe/2vq8oz.jpg"
YOUTUBE_IMG_URL = "https://files.catbox.moe/2vq8oz.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://files.catbox.moe/2vq8oz.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://files.catbox.moe/2vq8oz.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://files.catbox.moe/2vq8oz.jpg"

# Helper function
def time_to_seconds(time: str) -> int:
    return sum(int(x) * 60**i for i, x in enumerate(reversed(time.split(":"))))

# Calculate total duration limit in seconds
DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))

# Validate URLs
if SUPPORT_CHANNEL and not re.match(r"(?:http|https)://", SUPPORT_CHANNEL):
    raise SystemExit(
        "[ERROR] - Your SUPPORT_CHANNEL url is invalid. It must start with https://"
    )

if SUPPORT_CHAT and not re.match(r"(?:http|https)://", SUPPORT_CHAT):
    raise SystemExit(
        "[ERROR] - Your SUPPORT_CHAT url is invalid. It must start with https://"
    )
