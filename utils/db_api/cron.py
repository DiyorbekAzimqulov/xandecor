import asyncio
from aiogram.types import InputMediaPhoto
from keyboards.inline.users_inlines import get_products_kb_in
from loader import bot
from utils.db_api.connector_db import get_sales

DAILY_CRON_INTERVAL = 60 * 60 * 24 # 24 hours


async def ask_review_for_product():
    while True:
        await asyncio.sleep(DAILY_CRON_INTERVAL)
        sales = await get_sales()      
        for sale in sales:
            product, user, container = sale.product, sale.user, sale.container
            products_kb_in = await get_products_kb_in(
                product.id, user.telegram_id, container.id
            )
            file_path1 = product.image1.path
            file_path2 = product.image2.path
            
            caption = f"{product.name}\n{product.number}"
            try:
                with open(file_path1, "rb") as file1, open(file_path2, "rb") as file2:
                    media = [
                        InputMediaPhoto(file1, caption=caption),
                        InputMediaPhoto(file2)
                    ]
                    await bot.send_media_group(
                        chat_id=user.telegram_id,
                        media=media
                    )
                    await bot.send_message(
                        text='Boshqa mahsulotlarni ko\'rish uchun quyidagi tugmani bosing:',
                        chat_id=user.telegram_id,
                        reply_markup=products_kb_in
                    )
            except Exception as e:
                print(e)
                await bot.send_message(user.telegram_id, caption)
