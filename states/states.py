from aiogram.fsm.state import State, StatesGroup

class WeatherStates(StatesGroup):
    """Стани для отримання погоди"""
    waiting_for_city = State()

class CartStates(StatesGroup):
    """Стани для роботи з кошиком"""
    cart_management = State()
    waiting_for_item_to_remove = State()
    
class OrderStates(StatesGroup):
    """Стани для оформлення замовлення"""
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_currency = State()
    waiting_for_delivery = State()
    waiting_for_payment = State()

class AdminStates(StatesGroup):
    """Стани для адміністративних функцій"""
    waiting_for_category = State()
    waiting_for_car_name = State() 
    waiting_for_price = State()
    waiting_for_image_url = State()
    waiting_for_car_to_remove = State()