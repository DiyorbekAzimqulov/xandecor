import asyncio
from orm.settings import DAILY_CRON_INTERVAL
from salebot.utils.db_api.connector_db import get_sales_by_deadline
from salebot.loader import bot

async def notify_users_deadline():
    while True:
        await asyncio.sleep(DAILY_CRON_INTERVAL)
        print("Checking for sales deadlines...")
        sales = await get_sales_by_deadline()
        for sale in sales:
            if sale.user and sale.user.telegram_id:
                await bot.send_message(
                    chat_id=sale.user.telegram_id,
                    text=f"⚠️ {sale.user.name} buyurtmangizni to'lov muddati yakunlanmoqda! ⚠️\n\n"
                         f"📦 Mahsulot: {sale.product.name}\n"
                         f"💵 Narxi: {sale.price} $\n"
                         f"🕒 Muddati: {sale.deadline}\n\n"
                )