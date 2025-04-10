from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import logging
import re

from database.database import add_new_car, remove_car, get_all_cars
from states.states import AdminStates

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Обробник команди /admin"""
    user_name = message.from_user.first_name
    logger.info(f"Користувач {user_name} запустив команду /admin")
    
    admin_text = (
        "🔐 <b>Адміністративна панель</b> 🔐\n\n"
        "Доступні команди:\n"
        "🔹 /add_car - Додати новий автомобіль в базу даних\n"
        "🔹 /remove_car - Видалити автомобіль з бази даних"
    )
    
    await message.answer(admin_text, parse_mode="HTML")
    logger.info(f"Користувачу {user_name} відправлено адміністративне меню")

@router.message(Command("add_car"))
async def cmd_add_car(message: Message, state: FSMContext):
    """Обробник команди /add_car"""
    user_name = message.from_user.first_name
    logger.info(f"Користувач {user_name} запустив команду /add_car")
    
    await message.answer("Введіть категорію автомобіля:")
    await state.set_state(AdminStates.waiting_for_category)
    logger.info(f"Для користувача {user_name} встановлено стан AdminStates.waiting_for_category")

@router.message(AdminStates.waiting_for_category)
async def handle_category_input(message: Message, state: FSMContext):
    """Обробник введення категорії автомобіля"""
    user_name = message.from_user.first_name
    category = message.text
    logger.info(f"Користувач {user_name} ввів категорію: {category}")
    
    await state.update_data(category=category)
    
    await message.answer("Введіть назву автомобіля:")
    await state.set_state(AdminStates.waiting_for_car_name)
    logger.info(f"Для користувача {user_name} встановлено стан AdminStates.waiting_for_car_name")

@router.message(AdminStates.waiting_for_car_name)
async def handle_car_name_input(message: Message, state: FSMContext):
    """Обробник введення назви автомобіля"""
    user_name = message.from_user.first_name
    car_name = message.text
    logger.info(f"Користувач {user_name} ввів назву автомобіля: {car_name}")
    
    await state.update_data(car_name=car_name)
    
    await message.answer("Введіть ціну автомобіля (в доларах):")
    await state.set_state(AdminStates.waiting_for_price)
    logger.info(f"Для користувача {user_name} встановлено стан AdminStates.waiting_for_price")

@router.message(AdminStates.waiting_for_price)
async def handle_price_input(message: Message, state: FSMContext):
    """Обробник введення ціни автомобіля"""
    user_name = message.from_user.first_name
    price_text = message.text
    logger.info(f"Користувач {user_name} ввів ціну: {price_text}")
    
    try:
        price = float(price_text)
        if price <= 0:
            await message.answer("Ціна повинна бути більше нуля. Будь ласка, введіть коректне значення:")
            return
    except ValueError:
        await message.answer("Будь ласка, введіть коректне числове значення для ціни:")
        logger.warning(f"Користувач {user_name} ввів некоректну ціну: {price_text}")
        return
    
    await state.update_data(price=price)
    
    await message.answer("Введіть URL-адресу зображення автомобіля:")
    await state.set_state(AdminStates.waiting_for_image_url)
    logger.info(f"Для користувача {user_name} встановлено стан AdminStates.waiting_for_image_url")

@router.message(AdminStates.waiting_for_image_url)
async def handle_image_url_input(message: Message, state: FSMContext):
    """Обробник введення URL-адреси зображення"""
    user_name = message.from_user.first_name
    image_url = message.text
    logger.info(f"Користувач {user_name} ввів URL зображення: {image_url}")
    
    url_pattern = r'^https?://.+\..+'
    if not re.match(url_pattern, image_url):
        await message.answer("Будь ласка, введіть коректний URL-адресу, що починається з http:// або https://:")
        logger.warning(f"Користувач {user_name} ввів некоректний URL: {image_url}")
        return
    
    state_data = await state.get_data()
    category = state_data.get("category")
    car_name = state_data.get("car_name")
    price = state_data.get("price")
    
    success = add_new_car(category, car_name, price, image_url)
    
    if success:
        await message.answer(f"Автомобіль '{car_name}' успішно додано до бази даних в категорію '{category}'.")
        logger.info(f"Користувач {user_name} успішно додав автомобіль {car_name}")
    else:
        await message.answer("Виникла помилка при додаванні автомобіля. Спробуйте ще раз пізніше.")
        logger.error(f"Помилка при додаванні автомобіля користувачем {user_name}")
    
    await state.clear()
    logger.info(f"Для користувача {user_name} очищено стан після додавання автомобіля")

@router.message(Command("remove_car"))
async def cmd_remove_car(message: Message, state: FSMContext):
    """Обробник команди /remove_car"""
    user_name = message.from_user.first_name
    logger.info(f"Користувач {user_name} запустив команду /remove_car")
    
    all_cars = get_all_cars()
    
    if not all_cars:
        await message.answer("В базі даних немає автомобілів.")
        return
    
    cars_list = "Доступні автомобілі:\n\n"
    for car in all_cars:
        cars_list += f"🚗 {car}\n"
    
    cars_list += "\nВведіть точну назву автомобіля, який потрібно видалити:"
    
    await message.answer(cars_list)
    await state.set_state(AdminStates.waiting_for_car_to_remove)
    logger.info(f"Для користувача {user_name} встановлено стан AdminStates.waiting_for_car_to_remove")

@router.message(AdminStates.waiting_for_car_to_remove)
async def handle_car_to_remove(message: Message, state: FSMContext):
    """Обробник введення назви автомобіля для видалення"""
    user_name = message.from_user.first_name
    car_name = message.text
    logger.info(f"Користувач {user_name} хоче видалити автомобіль: {car_name}")
    
    success = remove_car(car_name)
    
    if success:
        await message.answer(f"Автомобіль '{car_name}' успішно видалено з бази даних.")
        logger.info(f"Користувач {user_name} успішно видалив автомобіль {car_name}")
    else:
        await message.answer(f"Автомобіль '{car_name}' не знайдено в базі даних або виникла помилка при видаленні.")
        logger.warning(f"Помилка при видаленні автомобіля '{car_name}' користувачем {user_name}")
    
    await state.clear()
    logger.info(f"Для користувача {user_name} очищено стан після видалення автомобіля")