# import keyborads
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.db_api.connector_db import get_categories

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

async def categories_kb():
    categories = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=name_of_category)
            ] for name_of_category in [category.name for category in await get_categories()]
        ] + [
            [KeyboardButton(text="📋 Buyurtmalarim")]
        ],
        resize_keyboard=True
    )
    return categories

def get_user_phone_kb():
    user_phone_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Telefon raqamni yuborish", request_contact=True)
            ]
        ],
        resize_keyboard=True
    )
    return user_phone_kb

def store_kb():
    store_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📋 Buyurtmalarim")
            ],
        ],
        resize_keyboard=True
    )
    return store_kb

def cancel_volume_kb():
    cancel_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="❌ Bekor qilish")
            ],
        ],
        resize_keyboard=True
    )
    return cancel_kb