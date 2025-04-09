from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def get_categories_keyboard(categories):
    """Створення клавіатури для вибору категорії"""
    builder = ReplyKeyboardBuilder()
    for category in categories:
        builder.button(text=category)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def get_cars_keyboard(cars):
    """Створення інлайн-клавіатури для вибору автомобіля"""
    builder = InlineKeyboardBuilder()
    for car in cars:
        builder.button(text=car, callback_data=f"car_{car}")
    builder.adjust(1)
    return builder.as_markup()

def get_add_to_cart_keyboard(car):
    """Створення інлайн-клавіатури для додавання у кошик"""
    builder = InlineKeyboardBuilder()
    builder.button(text="Додати автомобіль у кошик", callback_data=f"add_to_cart_{car}")
    return builder.as_markup()

def get_cart_management_keyboard():
    """Створення клавіатури для управління кошиком"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="Видалити товар")
    builder.button(text="Очистити кошик")
    builder.button(text="Оформити замовлення")
    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)

def get_delivery_keyboard():
    """Створення клавіатури для вибору доставки"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="Експрес доставка")
    builder.button(text="Стандартна доставка")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

def get_currency_keyboard():
    """Створення клавіатури для вибору валюти"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="USD (Долари)")
    builder.button(text="UAH (Гривні)")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)