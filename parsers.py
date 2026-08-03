import asyncio
import yt_dlp

async def get_profile_videos(nickname_or_url: str) -> dict:
    """Парсить останні 10 відео з профілю TikTok/Instagram/YouTube"""
    
    # Якщо користувач скинув просто @nickname, робимо з нього лінк TikTok
    if nickname_or_url.startswith("@"):
        url = f"https://www.tiktok.com/{nickname_or_url}"
    else:
        url = nickname_or_url

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': False, # Щоб дістати всю статистику
        'playlist_items': '1-10', # Беремо ТІЛЬКИ останні 10 відео
        'no_warnings': True,
    }
    
    def fetch():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    try:
        info = await asyncio.to_thread(fetch)
        
        # Якщо це плейлист/профіль
        if 'entries' in info:
            videos = info['entries']
        else:
            videos = [info] # Якщо це лінк на 1 відео
            
        parsed_videos = []
        for v in videos:
            if not v: continue
            parsed_videos.append({
                "title": v.get("title", "Без названия")[:30] + "...",
                "views": int(v.get("view_count", 0) or 0),
                "likes": int(v.get("like_count", 0) or 0),
                "comments": int(v.get("comment_count", 0) or 0),
                "shares": int(v.get("repost_count", 0) or 0),
                "upload_date": v.get("upload_date", "Неизвестно")
            })
            
        return {
            "status": "success",
            "account": info.get("uploader", nickname_or_url),
            "account_id": info.get("uploader_id", "Неизвестно"),
            "videos": parsed_videos
        }
    except Exception as e:
        return {"status": "error", "message": f"Ошибка доступа к профилю: {str(e)}"}
