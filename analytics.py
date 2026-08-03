import statistics

def calculate_er(views: int, likes: int, comments: int, shares: int = 0) -> float:
    """
    Engagement Rate (ER) - Коефіцієнт залученості.
    Показує, який відсоток глядачів взаємодіяв з відео.
    """
    if views <= 0:
        return 0.0
    
    total_engagements = likes + comments + shares
    er = (total_engagements / views) * 100
    return round(er, 2)

def calculate_lvr(views: int, likes: int) -> float:
    """
    Like-to-View Ratio (LVR) - Індекс віральності.
    Відсоток глядачів, які поставили лайк.
    """
    if views <= 0:
        return 0.0
        
    lvr = (likes / views) * 100
    return round(lvr, 2)

def calculate_clr(likes: int, comments: int) -> float:
    """
    Comment-to-Like Ratio (CLR) - Індекс дискусійності.
    Відсоток коментарів відносно лайків. 
    Високий CLR (>5%) означає, що контент провокує на обговорення.
    """
    if likes <= 0:
        return 0.0
        
    clr = (comments / likes) * 100
    return round(clr, 2)

def check_shadowban(current_views: int, historical_views: list[int]) -> dict:
    """
    Детектор тіньового бану (Shadowban).
    Порівнює перегляди останнього відео з медіаною попередніх.
    """
    # Якщо історії ще немає або вона замала, ми не можемо чесно оцінити бан
    if not historical_views or len(historical_views) < 3:
        return {
            "status": "Невідoмо", 
            "drop_rate": 0, 
            "message": "Недостатньо даних для аналізу."
        }

    # Рахуємо медіану (вона ігнорує випадкові "зальоти" на мільйон переглядів)
    median_views = statistics.median(historical_views)
    
    # Якщо медіана нульова, акаунт мертвий
    if median_views <= 0:
        return {
            "status": "Мертвий акаунт", 
            "drop_rate": 100, 
            "message": "Акаунт не збирає переглядів взагалі."
        }

    # Рахуємо відсоток падіння
    drop_rate = ((median_views - current_views) / median_views) * 100
    drop_rate = round(drop_rate, 2)

    # Визначаємо статус
    if drop_rate > 85:
        return {
            "is_banned": True,
            "drop_rate": drop_rate,
            "message": "🔴 Високий ризик тіньового бану (перегляди впали критично)."
        }
    elif drop_rate > 50:
        return {
            "is_banned": False,
            "drop_rate": drop_rate,
            "message": "🟡 Жовта зона: алгоритми гірше просувають це відео."
        }
    else:
        return {
            "is_banned": False,
            "drop_rate": drop_rate if drop_rate > 0 else 0,
            "message": "🟢 Все добре. Аномального падіння не виявлено."
        }

def analyze_video(raw_data: dict) -> dict:
    """
    Головна функція, яка об'єднує всі метрики для одного відео.
    """
    views = raw_data.get("views", 0)
    likes = raw_data.get("likes", 0)
    comments = raw_data.get("comments", 0)
    shares = raw_data.get("shares", 0)

    return {
        "er": calculate_er(views, likes, comments, shares),
        "lvr": calculate_lvr(views, likes),
        "clr": calculate_clr(likes, comments),
    }
