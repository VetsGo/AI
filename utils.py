import requests

def get_exchange_rate():
    """Отримання поточного курсу валют від ПриватБанку"""
    url = "https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5"
    response = requests.get(url)
    data = response.json()
    usd_rate = next(item for item in data if item["ccy"] == "USD")
    return float(usd_rate["buy"])