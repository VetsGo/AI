from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

from database import get_car_price, get_categories
from keyboards import get_cart_management_keyboard, get_categories_keyboard
from states import CartStates

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("cart"))
async def cmd_cart(message: Message, state: FSMContext):
    """Обробник команди /cart"""
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    logger.info(f"Користувач {user_name} запустив команду /cart")
    
    state_data = await state.get_data()
    cart_items = state_data.get("cart_items", [])
    
    if not cart_items:
        await message.answer("Ваш кошик порожній.")
        logger.info(f"Користувачу {user_name} показано повідомлення про порожній кошик")
        return
    
    cart_text = "🛒 Ваш кошик:\n\n"
    total_price = 0
    
    for car in cart_items:
        price = get_car_price(car)
        total_price += price
        cart_text += f"🚗 {car} - {price}$\n"
    
    cart_text += f"\nЗагальна сума: {total_price}$"
    
    await message.answer(cart_text)
    logger.info(f"Користувачу {user_name} показано кошик")
    
    await state.update_data(user_id=user_id)
    
    keyboard = get_cart_management_keyboard()
    await message.answer("Оберіть дію з кошиком:", reply_markup=keyboard)
    await state.set_state(CartStates.cart_management)
    logger.info(f"Для користувача {user_name} встановлено стан CartStates.cart_management")

@router.callback_query(F.data.startswith("add_to_cart_"))
async def handle_add_to_cart(callback: CallbackQuery, state: FSMContext):
    """Обробник додавання автомобіля у кошик"""
    user_name = callback.from_user.first_name
    user_id = callback.from_user.id
    car = callback.data.split("_")[3]
    logger.info(f"Користувач {user_name} додає у кошик автомобіль: {car}")
    
    state_data = await state.get_data()
    current_cart = state_data.get("cart_items", [])
    
    if car not in current_cart:
        current_cart.append(car)
        await state.update_data(cart_items=current_cart)
        logger.info(f"Автомобіль {car} додано до кошика користувача {user_name}")
        
        await callback.message.answer("Товар додано до кошику")
    else:
        await callback.message.answer("Цей автомобіль вже є у вашому кошику")
    
    await callback.answer()

@router.message(CartStates.cart_management, F.text == "Очистити кошик")
async def handle_clear_cart(message: Message, state: FSMContext):
    """Обробник очищення кошика"""
    user_name = message.from_user.first_name
    logger.info(f"Користувач {user_name} очищує кошик")
    
    await state.update_data(cart_items=[])
    
    await message.answer("Кошик успішно очищено.")
    logger.info(f"Кошик користувача {user_name} очищено")
    
    await state.clear()
    logger.info(f"Для користувача {user_name} очищено стан після очищення кошика")

@router.message(CartStates.cart_management, F.text == "Видалити товар")
async def handle_remove_item_request(message: Message, state: FSMContext):
    """Обробник запиту на видалення товару"""
    user_name = message.from_user.first_name
    logger.info(f"Користувач {user_name} хоче видалити товар з кошика")
    
    state_data = await state.get_data()
    cart_items = state_data.get("cart_items", [])
    if not cart_items:
        await message.answer("Ваш кошик порожній.")
        await state.clear()
        return
    
    items_text = "Введіть назву автомобіля, який хочете видалити:\n\n"
    for car in cart_items:
        items_text += f"🚗 {car}\n"
    
    await message.answer(items_text)
    await state.set_state(CartStates.waiting_for_item_to_remove)
    logger.info(f"Для користувача {user_name} встановлено стан CartStates.waiting_for_item_to_remove")

@router.message(CartStates.waiting_for_item_to_remove)
async def handle_remove_item(message: Message, state: FSMContext):
    """Обробник видалення конкретного товару"""
    user_name = message.from_user.first_name
    car_name = message.text
    logger.info(f"Користувач {user_name} видаляє товар: {car_name}")
    
    state_data = await state.get_data()
    cart_items = state_data.get("cart_items", [])
    
    if car_name in cart_items:
        cart_items.remove(car_name)
        await state.update_data(cart_items=cart_items)
        await message.answer(f"Автомобіль '{car_name}' видалено з кошика.")
        logger.info(f"Товар '{car_name}' видалено з кошика користувача {user_name}")
    
        if not cart_items:
            await message.answer("Ваш кошик тепер порожній.")
            await state.clear()
            return
        
        cart_text = "🛒 Оновлений кошик:\n\n"
        total_price = 0
        
        for car in cart_items:
            price = get_car_price(car)
            total_price += price
            cart_text += f"🚗 {car} - {price}$\n"
        
        cart_text += f"\nЗагальна сума: {total_price}$"
        
        await message.answer(cart_text)
    else:
        await message.answer(f"Автомобіль '{car_name}' не знайдено у кошику.")
        logger.warning(f"Спроба видалити неіснуючий товар '{car_name}' з кошика користувача {user_name}")
    
    keyboard = get_cart_management_keyboard()
    await message.answer("Оберіть дію з кошиком:", reply_markup=keyboard)
    await state.set_state(CartStates.cart_management)
    logger.info(f"Користувач {user_name} повернувся до стану управління кошиком")

@router.message(CartStates.cart_management, F.text == "Завершити")
async def handle_finish_cart_management(message: Message, state: FSMContext):
    """Обробник завершення управління кошиком"""
    user_name = message.from_user.first_name
    logger.info(f"Користувач {user_name} завершує управління кошиком")
    
    await message.answer("Ви вийшли з режиму управління кошиком.", reply_markup=get_categories_keyboard(get_categories()))
    await state.clear()
    logger.info(f"Для користувача {user_name} очищено стан після управління кошиком")