import asyncio
from aiogram import Bot, Dispatcher

from config.config import API_TOKEN, storage
from handlers import router
from utils.menu import set_bot_commands

async def main():
    """Основна функція для запуску бота"""
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=storage)
    
    dp.include_router(router)
    
    await set_bot_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())