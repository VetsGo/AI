import logging
from aiogram.fsm.storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)
logging.getLogger('aiogram').setLevel(logging.WARNING)

API_TOKEN = '8012371329:AAHGDd9vNVBCiiWEc_EKYc9FSHHNbMTq4ik'
PAYMENT_TOKEN = '2051251535:TEST:OTk5MDA4ODgxLTAwNQ'

storage = MemoryStorage()