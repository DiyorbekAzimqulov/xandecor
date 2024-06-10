from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher import FSMContext
from loader import dp
from utils.db_api.connector_db import (
    get_users,
)
from keyboards.default.users_replies import categories_kb, get_user_phone_kb
from keyboards.inline.users_inlines import get_products_kb_in
from states.userstates import UserState
from django.core.exceptions import ObjectDoesNotExist


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    telegram_id = message.from_user.id
    users = await get_users()
    categories = await categories_kb()
    user_phone_kb = get_user_phone_kb()
    if telegram_id == int("1180612659"):
        await message.answer("Nodirbek sizni ko'rganimdan xursandman!")
    elif telegram_id not in [user.telegram_id for user in users]:
        await message.answer(
            "Salom! Siz ro'yxatdan o'tmagansiz. Ro'yxatdan o'tish uchun telefon raqamingizni kiriting.",
            reply_markup=user_phone_kb,
        )
        return
    await message.answer(
        f"Salom, {message.from_user.full_name}!", reply_markup=categories
    )
 

