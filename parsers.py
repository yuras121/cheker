import asyncio
import re
import os
import yt_dlp
from googleapiclient.discovery import build

# Отримуємо ключ YouTube з файлу .env (про нього поговоримо пізніше)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

async def get_tiktok_stats(url: str) -> dict:
    """
    Парсинг TikTok (та Instagram) безкоштовно через yt-dlp.
    """
    # Налаштування парсера
    ydl_opts = {
        'quiet': True,              # Не виводити зайвий текст у консоль
        'skip_download': True,      # ВАЖЛИВО! Не качати відео, лише метадані
        'no_warnings': True,
        'extract_flat': False,
    }
    
    # Створюємо синхронну функцію для yt-dlp
    def fetch():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    try:
        # Запускаємо парсер в окремому потоці (to_thread), 
        # щоб він не "заморозив" бота для інших користувачів, поки чекає відповідь від TikTok
        info = await asyncio.to_thread(fetch)
        
        # Повертаємо чистий словник тільки з потрібними нам цифрами
        return {
            "status": "success",
            "platform": "TikTok / Instagram",
            "title": info.get("title", "Без назви"),
            "uploader": info.get("uploader", "Невідомо"),
            "views": int(info.get("view_count", 0) or 0),
            "likes": int(info.get("like_count", 0) or 0),
            "comments": int(info.get("comment_count", 0) or 0),
            "shares": int(info.get("repost_count", 0) or 0) # yt-dlp рахує репости
        }
    except Exception as e:
        # Якщо TikTok заблокував запит або відео видалено
        return {"status": "error", "message": f"Помилка парсингу: {str(e)}"}

def extract_youtube_id(url: str):
    """Шукає ID відео в будь-якому YouTube посиланні"""
    regex = r"(?:v=|\/([0-9A-Za-z_-]{11}).*|list=)"
    match = re.search(regex, url)
    return match.group(1) if match else None

async def get_youtube_stats(url: str) -> dict:
    """
    Парсинг YouTube Shorts через офіційне API (Швидко і надійно).
    """
    video_id = extract_youtube_id(url)
    if not video_id:
        return {"status": "error", "message": "Не вдалося знайти ID відео."}
        
    def fetch():
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        request = youtube.videos().list(part="snippet,statistics", id=video_id)
        return request.execute()
        
    try:
        response = await asyncio.to_thread(fetch)
        if not response.get('items'):
            return {"status": "error", "message": "Відео не знайдено або воно приватне."}
            
        item = response['items'][0]
        stats = item['statistics']
        snippet = item['snippet']
        
        return {
            "status": "success",
            "platform": "YouTube Shorts",
            "title": snippet.get('title', 'Без назви'),
            "uploader": snippet.get('channelTitle', 'Невідомо'),
            "views": int(stats.get('viewCount', 0)),
            "likes": int(stats.get('likeCount', 0)),
            "comments": int(stats.get('commentCount', 0)),
            "shares": 0 # YouTube API не віддає кількість поширень
        }
    except Exception as e:
         return {"status": "error", "message": f"Помилка YouTube API: {str(e)}"}
