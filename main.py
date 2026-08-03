import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

import handlers
import database

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # 1. Ініціалізуємо базу даних (створюємо таблиці)
    await database.init_db()
    print("🗄 База данных подключена!")
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(handlers.router)
    
    print("🚀 PRO Бот успешно запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
