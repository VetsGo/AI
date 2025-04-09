import sqlite3
from typing import List, Dict, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)

conn = sqlite3.connect('cars.db', check_same_thread=False)
cursor = conn.cursor()

def init_db():
    """Ініціалізація бази даних та створення таблиць"""
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                car TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                image_url TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                car_id INTEGER NOT NULL,
                delivery_method TEXT NOT NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (car_id) REFERENCES cars (id)
            )
        ''')
        
        conn.commit()
        logger.info("База даних успішно ініціалізована")
    except Exception as e:
        logger.error(f"Помилка при ініціалізації бази даних: {str(e)}")
        conn.rollback()

init_db()

def get_categories() -> List[str]:
    """Отримання всіх категорій автомобілів"""
    cursor.execute("SELECT DISTINCT category FROM cars")
    categories = cursor.fetchall()
    return [category[0] for category in categories]

def get_cars_by_category(category: str) -> List[str]:
    """Отримання автомобілів за категорією"""
    cursor.execute("SELECT car FROM cars WHERE category = ?", (category,))
    cars = cursor.fetchall()
    return [car[0] for car in cars]

def get_car_info(car: str) -> Tuple[str, float, str]:
    """Отримання інформації про конкретний автомобіль"""
    cursor.execute("SELECT car, price, image_url FROM cars WHERE car = ?", (car,))
    car_info = cursor.fetchone()
    return car_info

def get_car_id(car: str) -> int:
    """Отримання ID автомобіля за назвою"""
    cursor.execute("SELECT id FROM cars WHERE car = ?", (car,))
    result = cursor.fetchone()
    return result[0] if result else None

def add_customer(name: str, phone: str) -> int:
    """Додавання нового користувача до бази даних"""
    try:
        cursor.execute("SELECT id FROM customers WHERE phone = ?", (phone,))
        existing_customer = cursor.fetchone()
        
        if existing_customer:
            customer_id = existing_customer[0]
            cursor.execute("UPDATE customers SET name = ? WHERE id = ?", (name, customer_id))
            conn.commit()
            logger.info(f"Оновлено дані існуючого користувача з ID: {customer_id}")
            return customer_id
        else:
            cursor.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", (name, phone))
            conn.commit()
            customer_id = cursor.lastrowid
            logger.info(f"Додано нового користувача з ID: {customer_id}")
            return customer_id
    except Exception as e:
        logger.error(f"Помилка при додаванні/оновленні користувача: {str(e)}")
        conn.rollback()
        return None

def create_order(customer_id: int, car_names: List[str], delivery_method: str) -> bool:
    """Створення замовлення для кількох автомобілів"""
    try:
        for car_name in car_names:
            car_id = get_car_id(car_name)
            if car_id:
                cursor.execute(
                    "INSERT INTO orders (customer_id, car_id, delivery_method) VALUES (?, ?, ?)",
                    (customer_id, car_id, delivery_method)
                )
        conn.commit()
        logger.info(f"Створено замовлення для користувача {customer_id} з {len(car_names)} автомобілями")
        return True
    except Exception as e:
        logger.error(f"Помилка при створенні замовлення: {str(e)}")
        conn.rollback()
        return False

def get_car_price(car_name: str) -> float:
    """Отримання ціни автомобіля за назвою"""
    cursor.execute("SELECT price FROM cars WHERE car = ?", (car_name,))
    result = cursor.fetchone()
    return result[0] if result else 0.0

def get_orders_by_customer(customer_id: int) -> List[Dict[str, Any]]:
    """Отримання всіх замовлень користувача"""
    cursor.execute("""
        SELECT o.id, c.car, c.price, o.delivery_method, o.order_date 
        FROM orders o
        JOIN cars c ON o.car_id = c.id
        WHERE o.customer_id = ?
        ORDER BY o.order_date DESC
    """, (customer_id,))
    
    orders = []
    for row in cursor.fetchall():
        orders.append({
            'id': row[0],
            'car': row[1],
            'price': row[2],
            'delivery_method': row[3],
            'order_date': row[4]
        })
    
    return orders

def find_customer_by_phone(phone: str) -> Optional[Dict[str, Any]]:
    """Пошук користувача за номером телефону"""
    cursor.execute("SELECT id, name, phone FROM customers WHERE phone = ?", (phone,))
    result = cursor.fetchone()
    if result:
        return {
            'id': result[0],
            'name': result[1],
            'phone': result[2]
        }
    return None