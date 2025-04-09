from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import logging

from database import get_car_price, get_categories
from utils import get_exchange_rate
from keyboards import get_currency_keyboard, get_delivery_keyboard, get_categories_keyboard
from states import CartStates, OrderStates
from config import PAYMENT_TOKEN
from aiogram.types import LabeledPrice

router = Router()
logger = logging.getLogger(__name__)

@router.message(CartStates.cart_management, F.text == "Оформити замовлення")
async def handle_checkout_request(message: Message, state: FSMContext):
    """Обробник запиту на оформлення замовлення"""
    user_name = message.from_user.first_name
    logger.info(f"Користувач {user_name} хоче оформити замовлення")
    
    state_data = await state.get_data()
    cart_items = state_data.get("cart_items", [])
    
    if not cart_items:
        await message.answer("Ваш кошик порожній. Додайте товари перед оформленням замовлення.")
        await state.clear()
        return
    
    await message.answer("Для оформлення замовлення введіть ваше ім'я:")
    await state.set_state(OrderStates.waiting_for_name)
    logger.info(f"Для користувача {user_name} встановлено стан OrderStates.waiting_for_name")

@router.message(OrderStates.waiting_for_name)
async def handle_order_name(message: Message, state: FSMContext):
    """Обробник введення імені для замовлення"""
    user_name = message.from_user.first_name
    customer_name = message.text
    logger.info(f"Користувач {user_name} ввів ім'я для замовлення: {customer_name}")
    
    await state.update_data(customer_name=customer_name)
    
    await message.answer("Введіть ваш номер телефону:")
    await state.set_state(OrderStates.waiting_for_phone)
    logger.info(f"Для користувача {user_name} встановлено стан OrderStates.waiting_for_phone")

@router.message(OrderStates.waiting_for_phone)
async def handle_order_phone(message: Message, state: FSMContext):
    """Обробник введення номера телефону для замовлення"""
    user_name = message.from_user.first_name
    phone = message.text
    logger.info(f"Користувач {user_name} ввів номер телефону для замовлення: {phone}")
    
    await state.update_data(phone=phone)
    
    keyboard = get_currency_keyboard()
    await message.answer("Оберіть валюту для оплати:", reply_markup=keyboard)
    await state.set_state(OrderStates.waiting_for_currency)
    logger.info(f"Для користувача {user_name} встановлено стан OrderStates.waiting_for_currency")

@router.message(OrderStates.waiting_for_currency)
async def handle_order_currency(message: Message, state: FSMContext):
    """Обробник вибору валюти для замовлення"""
    user_name = message.from_user.first_name
    currency_option = message.text
    logger.info(f"Користувач {user_name} вибрав валюту: {currency_option}")
    
    if "USD" in currency_option:
        currency = "USD"
    elif "UAH" in currency_option:
        currency = "UAH"
    else:
        await message.answer("Будь ласка, виберіть одну із запропонованих валют")
        return
    
    await state.update_data(currency=currency)
    
    keyboard = get_delivery_keyboard()
    await message.answer("Оберіть спосіб доставки:", reply_markup=keyboard)
    await state.set_state(OrderStates.waiting_for_delivery)
    logger.info(f"Для користувача {user_name} встановлено стан OrderStates.waiting_for_delivery")

@router.message(OrderStates.waiting_for_delivery)
async def handle_order_delivery(message: Message, state: FSMContext):
    """Обробник вибору способу доставки для замовлення"""
    user_name = message.from_user.first_name
    delivery = message.text
    logger.info(f"Користувач {user_name} вибрав спосіб доставки: {delivery}")
    
    if delivery not in ["Експрес доставка", "Стандартна доставка"]:
        await message.answer("Будь ласка, виберіть один із запропонованих способів доставки")
        return
    
    state_data = await state.get_data()
    customer_name = state_data.get("customer_name")
    phone = state_data.get("phone")
    currency = state_data.get("currency", "USD")
    cart_items = state_data.get("cart_items", [])
    
    await state.update_data(delivery=delivery)
    
    try:
        total_price_usd = 0
        items_description = ""
        
        for car in cart_items:
            price = get_car_price(car)
            total_price_usd += price
            items_description += f"{car} - {price}$\n"
        
        if currency == "UAH":
            exchange_rate = get_exchange_rate()
            total_price = total_price_usd * exchange_rate
            currency_symbol = "₴"
            items_description = (
                f"{items_description}\n"
                f"Курс: 1$ = {exchange_rate}₴\n"
                f"Загальна сума: {total_price:.2f}₴"
            )
        else:
            total_price = total_price_usd
            currency_symbol = "$"
            items_description = f"{items_description}\nЗагальна сума: {total_price:.2f}$"
        
        await message.answer(f"Переходимо до оплати ({total_price:.2f} {currency_symbol})...")
        logger.info(f"Створюємо запит на оплату для користувача {user_name} на суму {total_price:.2f} {currency}")
        
        await message.bot.send_invoice(
            chat_id=message.chat.id,
            title="Оплата автомобілів",
            description=f"Оплата замовлення:\n{items_description}",
            payload=f"order:{customer_name}:{phone}:{delivery}:{currency}",
            provider_token=PAYMENT_TOKEN,
            currency=currency,
            prices=[
                LabeledPrice(label="Оплата замовлення", amount=int(total_price * 100))
            ],
            need_name=False,
            need_phone_number=False,
            need_email=False,
            need_shipping_address=False,
            is_flexible=False
        )
        
        await state.set_state(OrderStates.waiting_for_payment)
        logger.info(f"Для користувача {user_name} встановлено стан OrderStates.waiting_for_payment")
        
    except Exception as e:
        logger.error(f"Помилка при створенні запиту на оплату для користувача {user_name}: {str(e)}")
        await message.answer(
            "Виникла помилка при створенні запиту на оплату. Спробуйте ще раз пізніше.",
            reply_markup=get_categories_keyboard(get_categories())
        )
        await state.clear()