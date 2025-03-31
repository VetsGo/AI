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

def get_currency_keyboard():
    """Створення клавіатури для вибору валюти"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="USD")
    builder.button(text="UAH")
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)