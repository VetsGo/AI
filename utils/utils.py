import requests
from datetime import datetime

def get_exchange_rate():
    """Отримання поточного курсу валют від ПриватБанку"""
    url = "https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5"
    response = requests.get(url)
    data = response.json()
    usd_rate = next(item for item in data if item["ccy"] == "USD")
    return float(usd_rate["buy"])

def get_weather(city):
    """Отримання погоди для міста"""
    api_key = "55da40ed1620372fc5496f576e919316"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ua"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            current_date = datetime.now().strftime("%d.%m.%Y")
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"]
            wind_speed = data["wind"]["speed"]
            
            weather_info = (
                f"Погода в {city} на {current_date}:\n"
                f"Температура: {temp}°C\n"
                f"Вологість: {humidity}%\n"
                f"Опис: {description}\n"
                f"Швидкість вітру: {wind_speed} м/с"
            )
            return weather_info
        else:
            return "Не вдалося знайти місто. Перевірте правильність написання."
    except Exception as e:
        return f"Сталася помилка при отриманні погоди: {str(e)}"