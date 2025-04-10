from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
import logging
from aiogram.exceptions import TelegramForbiddenError
from database.database import get_categories
from keyboards.keyboards import get_categories_keyboard

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обробник команди /start"""
    user_name = message.from_user.first_name
    logger.info(f"Користувач {user_name} запустив бота командою /start")
    
    try:
        await message.answer(f"Вітаю вас! Я допоможу вам з покупкою автомобіля.")
        
        help_text = (
            "Доступні команди:\n\n"
            "🚗 /cars - Перегляд та покупка автомобілів різних категорій\n"
            "🛒 /cart - Ваш кошик з обраними автомобілями\n"
            "🛠️ /admin - Функції адміністратора для взаємодії з автомобілями\n"
            "🌤️ /weather - Отримання інформації про погоду в обраному місті"
        )
        
        await message.answer(help_text)
        logger.info(f"Користувачу {user_name} відправлено привітання та список команд")
    except TelegramForbiddenError:
        logger.warning(f"Користувач {user_name} заблокував бота")

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обробник команди /help"""
    user_name = message.from_user.first_name
    logger.info(f"Користувач {user_name} запустив команду /help")
    
    help_text = (
        "🚗 <b>Автомобільний бот</b> 🚗\n\n"
        "<b>Доступні команди:</b>\n"
        "🔹 /start - Початок роботи з ботом\n" 
        "🔹 /cars - Перегляд та покупка автомобілів різних категорій\n"
        "🔹 /cart - Ваш кошик з обраними автомобілями\n"
        "🔹 /admin - Функції адміністратора для взаємодії з автомобілями\n"
        "🔹 /weather - Отримання інформації про погоду в обраному місті\n\n"
        "Для вибору категорії автомобілів просто натисніть /cars і виберіть потрібну категорію."
    )
    
    await message.answer(help_text, parse_mode="HTML")
    logger.info(f"Користувачу {user_name} відправлено довідку")