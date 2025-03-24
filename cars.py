import telebot
from telebot import types
from functions import get_categories, get_cars_by_category, get_car_info, get_exchange_rate

#Токен бота Telegram
API_TOKEN = '7926527947:AAHnyVUOs5MKSix6DtpgZWW_1mJCHOoYEWk'
bot = telebot.TeleBot(API_TOKEN)

#Обробник команди /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id, f"Вітаю вас {user_name}!")
    
    #Створення клавіатури з категоріями автомобілів
    categories = get_categories()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for category in categories:
        markup.add(types.KeyboardButton(category))
    bot.send_message(message.chat.id, "Яка категорія автомобілів вас цікавить?", reply_markup=markup)

#Обробник вибору категорії
@bot.message_handler(func=lambda message: message.text in get_categories())
def handle_category(message):
    category = message.text

    #Створення кнопок з автомобілями вибраної категорії
    cars = get_cars_by_category(category)
    markup = types.InlineKeyboardMarkup()
    for car in cars:
        markup.add(types.InlineKeyboardButton(car, callback_data=f"car_{car}"))
    bot.send_message(message.chat.id, "Обирайте автомобіль цієї категорії:", reply_markup=markup)

#Обробник вибору автомобіля
@bot.callback_query_handler(func=lambda call: call.data.startswith('car_'))
def handle_car_selection(call):
    car = call.data.split("_")[1]
    car_info = get_car_info(car)
    car_name, price, image_url = car_info

    #Надсилаємо фото авто та запитуємо кількість днів оренди
    bot.send_photo(call.message.chat.id, image_url)
    msg = bot.send_message(call.message.chat.id, f"На скільки діб ви берете {car_name}?")
    bot.register_next_step_handler(msg, handle_rental_days, car_name, price)

#Обробник введення кількості діб оренди
def handle_rental_days(message, car_name, price):
    try:
        days = int(message.text)
        
        if days <= 0:
            msg = bot.send_message(message.chat.id, "Будь ласка, введіть кількість діб більшу за 0.")
            bot.register_next_step_handler(msg, handle_rental_days, car_name, price)
            return
        
        total_price = price * days

        #Пропонуємо вибір валюти
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("USD"))
        markup.add(types.KeyboardButton("UAH"))
        msg = bot.send_message(message.chat.id, f"Виберіть валюту, яка вас цікавить:", reply_markup=markup)
        bot.register_next_step_handler(msg, handle_currency_selection, car_name, total_price)
    except ValueError:
        msg = bot.send_message(message.chat.id, "Будь ласка, введіть правильну кількість діб.")
        bot.register_next_step_handler(msg, handle_rental_days, car_name, price)

#Обробник вибору валюти
def handle_currency_selection(message, car_name, total_price):
    if message.text == "UAH":
        exchange_rate = get_exchange_rate()
        total_price_uah = total_price * exchange_rate
        msg = bot.send_message(message.chat.id, f"Ціна прокату становить {total_price_uah:.2f}₴.\nВас влаштовує?")
        bot.register_next_step_handler(msg, handle_price_confirmation, car_name, total_price_uah)
    elif message.text == "USD":
        msg = bot.send_message(message.chat.id, f"Ціна прокату становить {total_price}$.\nВас влаштовує?")
        bot.register_next_step_handler(msg, handle_price_confirmation, car_name, total_price)
    else:
        msg = bot.send_message(message.chat.id, "Будь ласка, виберіть валюту: 'USD' або 'UAH'.")
        bot.register_next_step_handler(msg, handle_currency_selection, car_name, total_price)

#Обробник підтвердження ціни
def handle_price_confirmation(message, car_name, total_price):
    user_name = message.from_user.first_name
    if message.text.lower() == 'так':
        categories = get_categories()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for category in categories:
            markup.add(types.KeyboardButton(category))
        bot.send_message(message.chat.id, f"Дякую {user_name} за бронювання {car_name}!", reply_markup=markup)
    elif message.text.lower() == 'ні':
        categories = get_categories()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for category in categories:
            markup.add(types.KeyboardButton(category))
        bot.send_message(message.chat.id, "Обирайте категорію, що вас цікавить:", reply_markup=markup)
    else:
        msg = bot.send_message(message.chat.id, "Будь ласка, напишіть 'так' або 'ні'.")
        bot.register_next_step_handler(msg, handle_price_confirmation, car_name, total_price)

bot.polling(none_stop=True)