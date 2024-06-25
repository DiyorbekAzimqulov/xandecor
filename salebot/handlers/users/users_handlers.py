from keyboards.inline.users_inlines import (
    get_cancel_sale_kb_in,
    get_products_kb_in,
    get_child_product_kb_in,
)
from loader import dp, bot
from aiogram import types

from reviewbot.keyboards.inline.users_inlines import get_sp_child_product_kb_in
from salebot.keyboards.default.users_replies import cancel_volume_kb, categories_kb
from utils.db_api.connector_db import (
    cancel_sale,
    check_user_exist,
    get_categories,
    get_child_product_by_id,
    get_products_child,
    get_products_parent,
    get_user_by_telegram_id,
    get_user_sales,
    create_user_sale,
    save_new_user,
)
from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext
from salebot.states.userstates import SaleVolume
from aiogram.types import ReplyKeyboardRemove

async def get_file_urls(product):
    file_url1 = product.image1.url
    file_url2 = product.image2.url
    return file_url1, file_url2

async def show_user_sales(telegram_id):
    user = await get_user_by_telegram_id(telegram_id)
    user_sales = await get_user_sales(user)
    if not user_sales:
        await bot.send_message(
            text="📋 Sizning buyurtmalar ro'yxati bo'sh!",
            chat_id=telegram_id
        )
        return
    for sale in user_sales:
        cancel_sale_kb_in = get_cancel_sale_kb_in(sale.id, telegram_id)
        file_url1, file_url2 = await get_file_urls(sale.product)
        caption = f"🛒 <b>Mahsulot:</b> {sale.product.name}\n📦 <b>Model:</b> {sale.product.number}\n🔢 <b>Buyurtma soni:</b> {sale.volume}"
        media = [
            types.InputMediaPhoto(file_url1, caption=caption),
            types.InputMediaPhoto(file_url2)
        ]
        await bot.send_media_group(
            chat_id=telegram_id,
            media=media
        )
        await bot.send_message(
            text='❌ Buyurtmani bekor qilish!',
            chat_id=telegram_id,
            reply_markup=cancel_sale_kb_in
        )
    return

@dp.message_handler()
async def categories(message: types.Message):
    telegram_id = message.from_user.id
    category_text = message.text.strip()

    categories_list = await get_categories()
    category_names = [category.name for category in categories_list]
    if category_text == "📋 Buyurtmalarim":
        await show_user_sales(telegram_id)
        return
    if category_text not in category_names:
        await message.answer(
            "⚠️ Berilgan kategoriyada hech qanday mahsulot topilmadi! Iltimos, qaytadan urinib ko'ring!"
        )
        return
    products = await get_products_parent(category_text)

    for product in products:
        products_kb_in = await get_products_kb_in(product.id, telegram_id)
        file_url1, file_url2 = await get_file_urls(product)
        caption = f"📚 <b>Mahsulot turi:</b> {category_text}\n🛍️ <b>Mahsulot:</b> {product.name}\n🔢 <b>Model:</b> {product.number}"
        try:
            media = [
                types.InputMediaPhoto(file_url1, caption=caption),
                types.InputMediaPhoto(file_url2)
            ]
            await bot.send_media_group(
                chat_id=telegram_id,
                media=media
            )
            await bot.send_message(
                text='▶️ Boshqa mahsulotlarni ko\'rish uchun quyidagi tugmani bosing:',
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
            else:
                child_product_kb_in = await get_child_product_kb_in(
                    child_product.id, telegram_id
                )
            file_url1, file_url2 = await get_file_urls(child_product)
            caption = f"🛍️ <b>Mahsulot:</b> {child_product.name}\n🔢 <b>Model:</b> {child_product.number}"
            media = [
                types.InputMediaPhoto(file_url1, caption=caption),
                types.InputMediaPhoto(file_url2)
            ]
            await bot.send_media_group(
                chat_id=telegram_id,
                media=media
            )
            await bot.send_message(
                text='🛒 Mahsulotni sotib olish uchun quyidagi tugmani bosing:',
                chat_id=telegram_id,
                reply_markup=child_product_kb_in
            )
    except Exception as e:
        print("IN the Child product includes the error is: ", e)
        await query.answer("⚠️ Error")


@dp.callback_query_handler(lambda query: query.data.startswith("sale"), state=None)
async def usersale(query: CallbackQuery, state: FSMContext):
    try:
        _, child_product_id, telegram_id = query.data.split(":")
        await query.answer("✅ Buyurtma qabul qilindi!")
        await query.message.answer("🛒 Buyurtmangiz qabul qilindi! Iltimos, qancha sotib olishingizni <b>raqamlar</b> bilan yozing!", parse_mode="HTML", reply_markup=cancel_volume_kb())
        await state.update_data(child_product_id=child_product_id)
    except Exception as e:
        print("IN the Child product includes the error is: ", e)
        await query.answer("⚠️ Error")
    await SaleVolume.sale_volume.set()

@dp.message_handler(state=SaleVolume.sale_volume)
async def sale_volume(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    product_volume = message.text
    categories = await categories_kb()
    if product_volume == "❌ Bekor qilish":
        await message.answer("❌ Buyurtma bekor qilindi!", reply_markup=categories)
        await state.finish()
        return
    if not product_volume.isdigit():
        await message.answer("⚠️ Iltimos, faqat raqamlar kiriting!")
        await SaleVolume.sale_volume.set()
        return
    data = await state.get_data()
    child_product_id = data.get("child_product_id")
    user = await get_user_by_telegram_id(telegram_id)
    child_product = await get_child_product_by_id(child_product_id)
    sale = await create_user_sale(user, child_product, int(product_volume))
    categories = await categories_kb()
    await message.answer("✅ Buyurtma qabul qilindi! Siz buyurtmangizni 2 kun ichida bekor qilishingiz mumkin!", reply_markup=categories)
    await state.finish()
    return

@dp.callback_query_handler(lambda query: query.data.startswith("cancel"), state=None)
async def cancelsale(query: CallbackQuery, state: FSMContext):
    try:
        _, sale_id, telegram_id = query.data.split(":")
        await cancel_sale(sale_id)
        await query.answer("❌ Buyurtma bekor qilindi!")
        await bot.delete_message(chat_id=telegram_id, message_id=query.message.message_id)        
    except Exception as e:
        print("IN the Child product includes the error is: ", e)
        await query.answer("⚠️ Error")
