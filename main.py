import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiohttp import web  # Додано для створення мікро-сервера
from dotenv import load_dotenv

import handlers
import database

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Фейковий веб-сервер для Render, щоб він бачив відкритий порт
async def health_check(request):
    return web.Response(text="Bot is ALIVE and RUNNING!")

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Ініціалізуємо базу даних
    await database.init_db()
    print("🗄 База данных подключена!")
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(handlers.router)
    
    # === ХИТРІСТЬ ДЛЯ RENDER: Запускаємо веб-сервер ===
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render передає номер порту через змінну середовища PORT
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Фейковий веб-сервер запущено на порту {port}")
    # ===================================================

    print("🚀 PRO Бот успешно запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
