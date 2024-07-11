from salesdoctorbot.models import StockProduct, WareHouse, WareHouseProduct
from salesdoctorbot.salesDoctorAuth import auth_sales_doctor
from salesdoctorbot.services import getProducts_by_WH_Ca, update_sold_ostatok_stock
from salesdoctorbot.data.config import CATEGORY_ID, ADMINS
import asyncio
from asgiref.sync import sync_to_async
from salesdoctorbot.loader import bot
from django.db.models import Q
from salesdoctorbot.data.config import GROUP_ID

DAILY_REPORT_INTERVAL = 10  # seconds
TELEGRAM_MESSAGE_LIMIT = 4096  # Telegram message character limit
MINIMUM_OSTATOK = 26
MAXIMUM_OSTATOK = 32
CONS_ADD = 6


async def generate_daily_report() -> str:
    while True:
        await asyncio.sleep(DAILY_REPORT_INTERVAL)

        token, user_id = await sync_to_async(auth_sales_doctor)()
        if token and user_id:
            await sync_to_async(getProducts_by_WH_Ca)(token, user_id, CATEGORY_ID)
            
            report = "📊 <b>Kunlik Hisobot</b>"

            # General warehouse
            general_warehouse = await sync_to_async(WareHouse.objects.get)(name="Основной склад")
            general_products = await sync_to_async(lambda: list(WareHouseProduct.objects.filter(warehouse=general_warehouse)))()

            # All other warehouses
            warehouses = await sync_to_async(lambda: list(WareHouse.objects.exclude(name="Основной склад")))()

            for warehouse in warehouses:
                report += f"\n\n<b>{warehouse.name} omboriga</b>"
                await sync_to_async(update_sold_ostatok_stock)(token, user_id, warehouse.sd_id, CATEGORY_ID)
                warehouse_products = await sync_to_async(lambda: list(WareHouseProduct.objects.filter(warehouse=warehouse)))()
                
                for warehouse_product in warehouse_products:
                    product_name = await sync_to_async(lambda: warehouse_product.product.name)()
                    ostatok = warehouse_product.ostatok
                    general_product = next((gp for gp in general_products if gp.product == warehouse_product.product), None)

                    if ostatok <= MINIMUM_OSTATOK and general_product is not None and general_product.ostatok > 0:
                        missing_product = MAXIMUM_OSTATOK - ostatok
                        round_product = round(missing_product / CONS_ADD)
                        quantity = round_product * CONS_ADD
                        report += f"\n{product_name}: X{quantity} ta o'tqazish kerak!"
                    
            # Send the report in chunks to fit within Telegram's message limit
            report_chunks = [report[i:i + TELEGRAM_MESSAGE_LIMIT] for i in range(0, len(report), TELEGRAM_MESSAGE_LIMIT)]
            for chunk in report_chunks:
                await bot.send_message(1180612659, chunk)
        else:
            return "Autentifikatsiya muvaffaqiyatsiz o'tdi"
