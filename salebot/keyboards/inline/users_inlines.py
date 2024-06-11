# import inline keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# from utils.db_api.connector_db import

async def get_products_kb_in(product_id, telegram_id, container_id="None"):
    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.add(
        InlineKeyboardButton(
            text="🔍 Barcha turlari",
            callback_data=f"product:{product_id}:{telegram_id}:{container_id}",
        )
    )
    return inline_keyboard

async def get_child_product_kb_in(child_product_id, telegram_id):
    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.add(
        InlineKeyboardButton(
            text="🛒 Buyurtma berish",
            callback_data=f"sale:{child_product_id}:{telegram_id}"
        )
    )
    return inline_keyboard

def get_cancel_sale_kb_in(sale_id, telegram_id):
    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.add(
        InlineKeyboardButton(
            text="❌ Bekor qilish",
            callback_data=f"cancel_sale:{sale_id}:{telegram_id}"
        )
    )
    return inline_keyboard
