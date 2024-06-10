from keyboards.inline.users_inlines import (
    get_products_kb_in,
    get_child_product_kb_in,
    get_sp_child_product_kb_in,
)
from loader import dp, bot
from aiogram import types

from utils.db_api.connector_db import (
    check_user_exist,
    get_categories,
    get_child_product_by_id,
    get_products_child,
    get_products_parent,
    get_sale_by_cp_ids,
    get_user_by_telegram_id,
    rate_product,
    get_sale_by_cp_ids,
    save_new_user,
    update_review_count,
)
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext


@dp.message_handler()
async def categories(message: types.Message):
    telegram_id = message.from_user.id
    category_text = message.text.strip()

    categories_list = await get_categories()
    category_names = [category.name for category in categories_list]

    if category_text not in category_names:
        await message.answer(
            "Berilgan kategoriyada hech qanday mahsulot topilmadi! Iltimos, qaytadan urinib ko'ring!"
        )
        return

    products = await get_products_parent(category_text)

    for product in products:
        products_kb_in = await get_products_kb_in(product.id, telegram_id)
        file_path1 = product.image1.path
        file_path2 = product.image2.path
        caption = f"{category_text}\n{product.name}\n{product.number}"
        try:
            with open(file_path1, "rb") as file1, open(file_path2, "rb") as file2:
                # Send the first image with caption
                media = [
                        types.InputMediaPhoto(file1, caption=caption),
                        types.InputMediaPhoto(file2)
                    ]
                await bot.send_media_group(
                    chat_id=telegram_id,
                    media=media
                )
                await bot.send_message(
                    text='Boshqa mahsulotlarni ko\'rish uchun quyidagi tugmani bosing:',
                    chat_id=telegram_id,
                    reply_markup=products_kb_in
                )
        except Exception as e:
            print(e)
            await bot.send_message(telegram_id, caption)


@dp.callback_query_handler(lambda query: query.data.startswith("product"), state=None)
async def product(query: CallbackQuery, state: FSMContext):
    try:
        _, product_id, telegram_id, container_id = query.data.split(":")
        child_products = await get_products_child(product_id)
        for child_product in child_products:
            if container_id != "None":
                child_product_kb_in = await get_sp_child_product_kb_in(
                    child_product.id, telegram_id, container_id
                )
                print("\nInlined Keyboard: ", child_product_kb_in)
            else:
                child_product_kb_in = await get_child_product_kb_in(
                    child_product.id, telegram_id
                )
            file_path1 = child_product.image1.path
            file_path2 = child_product.image2.path
            caption = f"{child_product.name}\n{child_product.number}"
            with open(file_path1, "rb") as file1, open(file_path2, "rb") as file2:
                media = [
                    types.InputMediaPhoto(file1, caption=caption),
                    types.InputMediaPhoto(file2)
                ]
                await bot.send_media_group(
                    chat_id=telegram_id,
                    media=media
                )
                await bot.send_message(
                    text='Mahsulotni baholash uchun quyidagi tugmalardan birini tanlang:',
                    chat_id=telegram_id,
                    reply_markup=child_product_kb_in
                )
    except Exception as e:
        print("IN the Child product includes the error is: ", e)
        await query.answer("Error")


@dp.callback_query_handler(lambda query: query.data.startswith("rate"), state=None)
async def rate_of_product(query: CallbackQuery, state: FSMContext):
    try:
        _, child_product_id, rating, telegram_id = query.data.split(":")
        await query.answer(f"Siz {rating}ga baholadingiz!")
        # remove inline keyboard from message
        await bot.edit_message_reply_markup(
            chat_id=telegram_id, message_id=query.message.message_id
        )
        EXCELLENT = "EXCELLENT"
        MEDIUM = "MEDIUM"
        BAD = "BAD"
        if rating == "A'lo":
            rating = EXCELLENT
        elif rating == "Yaxshi":
            rating = MEDIUM
        elif rating == "Qoniqarsiz":
            rating = BAD
        try:
            child_product = await get_child_product_by_id(child_product_id)
            user = await get_user_by_telegram_id(telegram_id)
            await rate_product(user, child_product, rating)
        except Exception as e:
            print(e)
            await query.answer("Error")

    except Exception as e:
        print(e)
        await query.answer("Error")


@dp.callback_query_handler(lambda query: query.data.startswith("review"), state=None)
async def rate_of_product(query: CallbackQuery, state: FSMContext):
    try:
        _, child_product_id, rating, telegram_id, container_id = query.data.split(":")
        await query.answer(f"Siz {rating}ga baholadingiz!")
        # remove inline keyboard from message
        await bot.edit_message_reply_markup(
            chat_id=telegram_id, message_id=query.message.message_id
        )
        EXCELLENT = "EXCELLENT"
        MEDIUM = "MEDIUM"
        BAD = "BAD"
        if rating == "A'lo":
            rating = EXCELLENT
        elif rating == "Yaxshi":
            rating = MEDIUM
        elif rating == "Qoniqarsiz":
            rating = BAD
        try:
            child_product = await get_child_product_by_id(child_product_id)
            sale = await get_sale_by_cp_ids(child_product_id, container_id)
            user = await get_user_by_telegram_id(telegram_id)
            await rate_product(user, child_product, rating, sale)
            await update_review_count(sale)
        except Exception as e:
            print(e)
            await query.answer("Error")

    except Exception as e:
        print(e)
        await query.answer("Error")

@dp.message_handler(content_types=types.ContentType.CONTACT)
async def handle_contact(message: types.Message):
    contact = message.contact
    telegram_id = message.from_user.id
    firt_name = contact.first_name
    last_name = contact.last_name
    phone_number = contact.phone_number
    if await check_user_exist(phone_number=phone_number):
        await message.reply(f"Kechirasiz, {firt_name}! Siz ro'yxatdan o'tgansiz! Iltimos, kuting admin sizni qo'shadi!")
        return
    if firt_name is None:
        firt_name = "Mavjud emas"
    elif last_name is None:
        last_name = "Mavjud emas"
    await save_new_user(telegram_id=telegram_id, phone_number=phone_number, first_name=firt_name, last_name=last_name)
    # You can now use user_id and phone_number as needed
    await message.reply(f"Rahmat! Sizning telefon raqamingiz: {phone_number} qabul qilindi!\nIltimos, kuting admin sizni ro'yxatdan o'tkazadi!")
    # Save the phone number to the database
    
