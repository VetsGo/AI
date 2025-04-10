from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import logging

from states.states import WeatherStates
from utils.utils import get_weather

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("weather"))
async def cmd_weather(message: Message, state: FSMContext):
    """Обробник команди /weather"""
    user_name = message.from_user.first_name
    logger.info(f"Користувач {user_name} запустив команду /weather")
    
    await message.answer("Введіть місто, щоб отримати погоду")
    await state.set_state(WeatherStates.waiting_for_city)
    
    logger.info(f"Для користувача {user_name} встановлено стан WeatherStates.waiting_for_city")

@router.message(WeatherStates.waiting_for_city)
async def handle_city(message: Message, state: FSMContext):
    """Обробник введення міста для погоди"""
    user_name = message.from_user.first_name
    city = message.text
    logger.info(f"Користувач {user_name} запитує погоду для міста: {city}")
    
    weather_info = get_weather(city)
    await message.answer(weather_info)
    
    await state.clear()
    logger.info(f"Користувачу {user_name} відправлено інформацію про погоду в місті {city}")
    logger.debug(f"Для користувача {user_name} очищено стан після отримання погоди")