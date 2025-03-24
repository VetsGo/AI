import sqlite3
import requests

#Підключення до бази даних SQLite
conn = sqlite3.connect('cars.db', check_same_thread=False)
cursor = conn.cursor()

#Функція для отримання списку унікальних категорій автомобілів
def get_categories():
    cursor.execute("SELECT DISTINCT category FROM cars")
    categories = cursor.fetchall()
    return [category[0] for category in categories]

#Функція для отримання списку автомобілів за категорією
def get_cars_by_category(category):
    cursor.execute("SELECT car FROM cars WHERE category = ?", (category,))
    cars = cursor.fetchall()
    return [car[0] for car in cars]

#Функція для отримання інформації про автомобіль
def get_car_info(car):
    cursor.execute("SELECT car, price, image_url FROM cars WHERE car = ?", (car,))
    car_info = cursor.fetchone()
    return car_info

#Функція для отримання курсу обміну USD/UAH через API ПриватБанку
def get_exchange_rate():
    url = "https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5"
    response = requests.get(url)
    data = response.json()
    usd_rate = next(item for item in data if item["ccy"] == "USD")
    return float(usd_rate["buy"])