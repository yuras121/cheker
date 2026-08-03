from aiogram import Router, F, types
from aiogram.filters import CommandStart
import parsers
import analytics
import database

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    total = await database.get_total_checks()
    text = (
        "🔥 **PRO | Social Media Checker**\n\n"
        "Введите ссылку на профиль, видео или логин аккаунта.\n\n"
        "┏ **Поддерживаемые форматы:**\n"
        "┠ `@nickname`\n"
        "┠ `https://tiktok.com/@nickname`\n"
        "┠ `https://www.tiktok.com/@nickname`\n"
        "┗ И любые прямые ссылки на видео.\n\n"
        f"📊 *За все время бот проверил {total} аккаунтов.*"
    )
    await message.answer(text, parse_mode="Markdown")

@router.message(F.text)
async def analyze_input(message: types.Message):
    user_input = message.text.strip()
    
    msg = await message.answer("⏳ *Сканирую аккаунт и собираю последние 10 видео...*", parse_mode="Markdown")
    
    # Парсимо дані
    raw_data = await parsers.get_profile_videos(user_input)
    
    if raw_data.get("status") == "error":
        await msg.edit_text(f"❌ **Ошибка:** {raw_data.get('message')}\n\nВозможно, аккаунт приватный или удален.", parse_mode="Markdown")
        return

    # Збільшуємо лічильник перевірок в базі
    await database.increment_checks()
    
    videos = raw_data['videos']
    if not videos:
        await msg.edit_text("❌ В этом профиле нет доступных видео.", parse_mode="Markdown")
        return

    # Збираємо історію переглядів для розрахунку Тіньового бану
    history_views = [v['views'] for v in videos]
    
    # Формуємо шапку звіту
    report = (
        f"👤 **Чекаю:** `{raw_data['account']}`\n"
        f"🆔 **ID:** `{raw_data['account_id']}`\n\n"
    )
    
    total_views, total_likes, total_comments = 0, 0, 0

    # Проходимося по кожному з 10 відео
    for i, v in enumerate(videos, start=1):
        # Математика для конкретного відео
        metrics = analytics.analyze_video(v)
        shadow_check = analytics.check_shadowban(v['views'], history_views)
        
        # Визначаємо статус бану для виводу
        ban_status = "Да 🔴" if shadow_check.get("is_banned") else "Нет 🟢"
        
        report += (
            f"🎬 **{i} видео:**\n"
            f"🕒 Загружено: `{v['upload_date']}`\n"
            f"👻 Теневой бан: **{ban_status}**\n"
            f"👁 `{v['views']:,}`  | ❤️ `{v['likes']:,}` | 💬 `{v['comments']:,}` | 🔁 `{v['shares']:,}`\n"
            f"📈 ER: **{metrics['er']}%** | LVR: **{metrics['lvr']}%**\n\n"
        )
        
        total_views += v['views']
        total_likes += v['likes']
        total_comments += v['comments']

    # Загальна статистика профілю
    avg_er = analytics.calculate_er(total_views, total_likes, total_comments)
    report += (
        f"➖➖➖➖➖➖➖➖➖➖\n"
        f"📊 **Общая статистика ({len(videos)} видео):**\n"
        f"👁 `{total_views:,}` | ❤️ `{total_likes:,}` | 💬 `{total_comments:,}`\n"
        f"🏆 **Средний ER аккаунта:** `{avg_er}%`"
    )

    # Якщо текст вийшов занадто довгим для Telegram (більше 4096 символів)
    if len(report) > 4000:
        report = report[:4000] + "\n\n...[Отчет обрезан]"

    await msg.edit_text(report, parse_mode="Markdown")
