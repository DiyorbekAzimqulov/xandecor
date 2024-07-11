from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher import FSMContext
from loader import dp
from django.core.exceptions import ObjectDoesNotExist


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    telegram_id = message.from_user.id
    if telegram_id == int("1180612659"):
        await message.answer("Nodirbek sizni ko'rganimdan xursandman!")
        return
    await message.answer("Assalomu alaykum Xan Decor kompaniyasining rasmiy botiga xush kelibsiz! Ushbu bot faqat Xan Decor kompaniyasi Hodimlari uchun ishlaydi. Siz ushbu botni ishlatishingiz mumkin!\nhttps://t.me/KhanDecorbot")
    return
