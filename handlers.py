from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import get_categories, get_cars_by_category, get_car_info
from keyboards import get_categories_keyboard, get_cars_keyboard, get_currency_keyboard
from states import RentalStates, WeatherStates
from utils import get_exchange_rate, get_weather

router = Router()

from aiogram.exceptions import TelegramForbiddenError

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обробник команди /start"""
    user_name = message.from_user.first_name
    try:
        await message.answer(f"Вітаю вас {user_name}!")
        
        help_text = (
            "Доступні команди:\n\n"
            "🚗 /cars - Перегляд та оренда автомобілів різних категорій\n"
            "🌤️ /weather - Отримання інформації про погоду в обраному місті"
        )
        
        await message.answer(help_text)
    except TelegramForbiddenError:
        print(f"Користувач {message.from_user.id} заблокував бота.")

@router.message(Command("cars"))
async def cmd_cars(message: Message):
    """Обробник команди /cars"""
    categories = get_categories()
    keyboard = get_categories_keyboard(categories)

    await message.answer(
        "Яка категорія автомобілів вас цікавить?", 
        reply_markup=keyboard
    )

@router.message(Command("weather"))
async def cmd_weather(message: Message, state: FSMContext):
    """Обробник команди /weather"""
    await message.answer("Введіть місто, щоб отримати погоду")
    await state.set_state(WeatherStates.waiting_for_city)

@router.message(WeatherStates.waiting_for_city)
async def handle_city(message: Message, state: FSMContext):
    """Обробник введення міста для погоди"""
    city = message.text
    weather_info = get_weather(city)
    await message.answer(weather_info)
    await state.clear()

@router.message(F.text.in_(get_categories()))
async def handle_category(message: Message):
    """Обробник вибору категорії"""
    category = message.text
    cars = get_cars_by_category(category)
    
    keyboard = get_cars_keyboard(cars)
    
    await message.answer(
        "Обирайте автомобіль цієї категорії:",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("car_"))
async def handle_car_selection(callback: CallbackQuery, state: FSMContext):
    """Обробник вибору автомобіля"""
    car = callback.data.split("_")[1]
    car_info = get_car_info(car)
    car_name, price, image_url = car_info
    
    await state.update_data(car_name=car_name, price=price)
    
    await callback.message.answer_photo(image_url)
    await callback.message.answer(f"На скільки діб ви берете {car_name}?")
    
    await state.set_state(RentalStates.waiting_for_days)
    
    await callback.answer()

@router.message(RentalStates.waiting_for_days)
async def handle_rental_days(message: Message, state: FSMContext):
    """Обробник введення кількості днів оренди"""
    try:
        days = int(message.text)
        
        if days <= 0:
            await message.answer("Будь ласка, введіть кількість діб більшу за 0.")
            return
        
        data = await state.get_data()
        car_name = data.get("car_name")
        price = data.get("price")
        
        total_price = price * days
        
        await state.update_data(total_price=total_price)
        
        keyboard = get_currency_keyboard()
        
        await message.answer(
            "Виберіть валюту, яка вас цікавить:",
            reply_markup=keyboard
        )
        
        await state.set_state(RentalStates.waiting_for_currency)
        
    except ValueError:
        await message.answer("Будь ласка, введіть правильну кількість діб.")

@router.message(RentalStates.waiting_for_currency)
async def handle_currency_selection(message: Message, state: FSMContext):
    """Обробник вибору валюти"""
    data = await state.get_data()
    car_name = data.get("car_name")
    total_price = data.get("total_price")
    
    if message.text == "UAH":
        exchange_rate = get_exchange_rate()
        total_price_uah = total_price * exchange_rate
        await state.update_data(total_price=total_price_uah, currency="₴")
        await message.answer(f"Ціна прокату становить {total_price_uah:.2f}₴.\nВас влаштовує?")
    elif message.text == "USD":
        await state.update_data(currency="$")
        await message.answer(f"Ціна прокату становить {total_price}$.\nВас влаштовує?")
    else:
        await message.answer("Будь ласка, виберіть валюту: 'USD' або 'UAH'.")
        return
    
    await state.set_state(RentalStates.waiting_for_confirmation)

@router.message(RentalStates.waiting_for_confirmation)
async def handle_price_confirmation(message: Message, state: FSMContext):
    """Обробник підтвердження ціни"""
    user_name = message.from_user.first_name
    data = await state.get_data()
    car_name = data.get("car_name")
    
    categories = get_categories()
    keyboard = get_categories_keyboard(categories)
    
    if message.text.lower() == 'так':
        await message.answer(
            f"Дякую {user_name} за бронювання {car_name}!",
            reply_markup=keyboard
        )
        await state.clear()
    elif message.text.lower() == 'ні':
        await message.answer(
            "Обирайте категорію, що вас цікавить:",
            reply_markup=keyboard
        )
        await state.clear()
    else:
        await message.answer("Будь ласка, напишіть 'так' або 'ні'.")