import sqlite3

conn = sqlite3.connect('cars.db', check_same_thread=False)
cursor = conn.cursor()

def get_categories():
    """Отримання всіх категорій автомобілів"""
    cursor.execute("SELECT DISTINCT category FROM cars")
    categories = cursor.fetchall()
    return [category[0] for category in categories]

def get_cars_by_category(category):
    """Отримання автомобілів за категорією"""
    cursor.execute("SELECT car FROM cars WHERE category = ?", (category,))
    cars = cursor.fetchall()
    return [car[0] for car in cars]

def get_car_info(car):
    """Отримання інформації про конкретний автомобіль"""
    cursor.execute("SELECT car, price, image_url FROM cars WHERE car = ?", (car,))
    car_info = cursor.fetchone()
    return car_info