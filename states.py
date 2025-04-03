from aiogram.fsm.state import State, StatesGroup

class RentalStates(StatesGroup):
    """Стани для процесу оренди автомобіля"""
    waiting_for_days = State()
    waiting_for_currency = State()
    waiting_for_confirmation = State()

class WeatherStates(StatesGroup):
    """Стани для отримання погоди"""
    waiting_for_city = State()