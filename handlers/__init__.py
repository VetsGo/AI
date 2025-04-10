from aiogram import Router
from .basic import router as basic_router
from .catalog import router as catalog_router
from .cart import router as cart_router
from .order import router as order_router
from .payment import router as payment_router
from .weather import router as weather_router
from .admin import router as admin_router

router = Router()
router.include_router(basic_router)
router.include_router(catalog_router)
router.include_router(cart_router)
router.include_router(order_router)
router.include_router(payment_router)
router.include_router(weather_router)
router.include_router(admin_router)