from aiogram import Router
from aiogram.types import Message, PreCheckoutQuery
from aiogram.fsm.context import FSMContext
from aiogram.types.message import ContentType
import logging

from database import add_customer, create_order, get_categories
from keyboards import get_categories_keyboard

router = Router()
logger = logging.getLogger(__name__)

@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    """Обробник підтвердження перевірки перед оплатою"""
    user_name = pre_checkout_query.from_user.first_name
    logger.info(f"Підтвердження платежу для користувача {user_name}")
    
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    logger.info(f"Платіж підтверджено для користувача {user_name}")

@router.message(lambda message: message.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: Message, state: FSMContext):
    """Обробник успішної оплати"""
    user_name = message.from_user.first_name
    logger.info(f"Користувач {user_name} успішно здійснив оплату")
    
    state_data = await state.get_data()
    customer_name = state_data.get("customer_name")
    phone = state_data.get("phone")
    delivery = state_data.get("delivery")
    cart_items = state_data.get("cart_items", [])
    
    try:
        customer_id = add_customer(customer_name, phone)
        
        if customer_id:
            order_created = create_order(customer_id, cart_items, delivery)
            
            if order_created:
                logger.info(f"Створено замовлення для користувача {user_name} з ID: {customer_id}")
            
                await state.update_data(cart_items=[])
                logger.info(f"Кошик користувача {user_name} очищено після оформлення замовлення")
                
                await message.answer(
                    "Оплата пройшла успішно! Дякуємо за покупку.",
                    reply_markup=get_categories_keyboard(get_categories())
                )
            else:
                logger.error(f"Помилка при створенні замовлення для користувача {user_name}")
                await message.answer(
                    "Оплата пройшла успішно, але виникла помилка при оформленні замовлення. Наш менеджер зв'яжеться з вами.",
                    reply_markup=get_categories_keyboard(get_categories())
                )
        else:
            logger.error(f"Помилка при створенні/оновленні користувача {customer_name}")
            await message.answer(
                "Оплата пройшла успішно, але виникла помилка при оформленні замовлення. Наш менеджер зв'яжеться з вами.",
                reply_markup=get_categories_keyboard(get_categories())
            )
        
        await state.clear()
        logger.info(f"Для користувача {user_name} очищено стан після оформлення замовлення")
        
    except Exception as e:
        logger.error(f"Помилка при створенні замовлення для користувача {user_name} після оплати: {str(e)}")
        await message.answer(
            "Оплата пройшла успішно, але виникла помилка при оформленні замовлення. Наш менеджер зв'яжеться з вами.",
            reply_markup=get_categories_keyboard(get_categories())
        )
        await state.clear()