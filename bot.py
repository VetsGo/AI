import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession

from config import API_TOKEN, storage
from handlers import router

async def main():
    """Основна функція для запуску бота"""
    session = AiohttpSession(proxy="http://proxy.server:3128")
    bot = Bot(token=API_TOKEN, session=session)
    dp = Dispatcher(storage=storage)
    
    dp.include_router(router)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())