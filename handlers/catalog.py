from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
import logging

from database import get_categories, get_cars_by_category, get_car_info
from keyboards import get_categories_keyboard, get_cars_keyboard, get_add_to_cart_keyboard

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("cars"))
async def cmd_cars(message: Message):
    """Обробник команди /cars"""
    user_name = message.from_user.first_name
    logger.info(f"Користувач {user_name} запустив команду /cars")
    
    categories = get_categories()
    keyboard = get_categories_keyboard(categories)
    
    logger.debug(f"Отримано категорії автомобілів: {categories}")

    await message.answer(
        "Яка категорія автомобілів вас цікавить?", 
        reply_markup=keyboard
    )
    logger.info(f"Користувачу {user_name} відправлено клавіатуру з категоріями автомобілів")

@router.message(F.text.in_(get_categories()))
async def handle_category(message: Message):
    """Обробник вибору категорії"""
    user_name = message.from_user.first_name
    category = message.text
    logger.info(f"Користувач {user_name} вибрав категорію: {category}")
    
    cars = get_cars_by_category(category)
    logger.debug(f"Отримано автомобілі для категорії {category}: {cars}")
    
    keyboard = get_cars_keyboard(cars)
    
    await message.answer(
        "Обирайте автомобіль цієї категорії:",
        reply_markup=keyboard
    )
    logger.info(f"Користувачу {user_name} відправлено клавіатуру з автомобілями категорії {category}")

@router.callback_query(F.data.startswith("car_"))
async def handle_car_selection(callback: CallbackQuery):
    """Обробник вибору автомобіля"""
    user_name = callback.from_user.first_name
    car = callback.data.split("_")[1]
    logger.info(f"Користувач {user_name} вибрав автомобіль: {car}")
    
    car_info = get_car_info(car)
    car_name, price, image_url = car_info
    logger.debug(f"Отримано інформацію про автомобіль {car}: ціна {price}, URL {image_url}")
    
    keyboard = get_add_to_cart_keyboard(car_name)
    
    try:
        await callback.message.answer_photo(
            image_url, 
            caption=f"Ціна даного автомобіля {price} доларів",
            reply_markup=keyboard
        )
        logger.info(f"Користувачу {user_name} відправлено фото та інформацію про автомобіль {car_name}")
    except Exception as e:
        logger.error(f"Помилка при відправці фото автомобіля {car_name}: {str(e)}")
        await callback.message.answer(
            f"Ціна даного автомобіля {price} доларів",
            reply_markup=keyboard
        )
    
    await callback.answer()