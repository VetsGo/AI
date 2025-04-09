
from aiogram.types import BotCommand

async def set_bot_commands(bot):
    """Налаштування меню команд бота"""
    commands = [
        BotCommand(command="start", description="Початок роботи з ботом"),
        BotCommand(command="cars", description="Перегляд та покупка автомобілів"),
        BotCommand(command="cart", description="Ваш кошик з обраними автомобілями"),
        BotCommand(command="weather", description="Інформація про погоду"),
        BotCommand(command="help", description="Отримати довідку")
    ]
    await bot.set_my_commands(commands)