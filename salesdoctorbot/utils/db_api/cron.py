import asyncio
from asgiref.sync import sync_to_async
from salesdoctorbot.loader import bot
from salesdoctorbot.models import WareHouse, WareHouseProduct
from salesdoctorbot.salesDoctorAuth import auth_sales_doctor
from salesdoctorbot.services import getProducts_by_WH_Ca, update_sold_ostatok_stock
from salesdoctorbot.data.config import CATEGORY_ID, GROUP_ID
from salesdoctorbot.reports_db import ship_db_data, ship_products, redistribute_products, redistribute_data

DAILY_SHIP_REPORT_INTERVAL = 50000 # seconds
DAILY_REDISTRIBUTE_REPORT = 15 # seconds
TELEGRAM_MESSAGE_LIMIT = 4096  # Telegram message character limit

async def daily_shipping_report() -> str:
    while False:
        await asyncio.sleep(DAILY_SHIP_REPORT_INTERVAL)
        print("Daily shipping report started")
        
        token, user_id = await sync_to_async(auth_sales_doctor)()
        if token and user_id:
            await sync_to_async(getProducts_by_WH_Ca)(token, user_id, CATEGORY_ID)
            
            # All other warehouses
            warehouses = await sync_to_async(lambda: list(WareHouse.objects.all()))()
            for warehouse in warehouses:
                order_ids = await sync_to_async(lambda: list(WareHouseProduct.objects.filter(warehouse=warehouse).values_list('product__sd_id', flat=True)))()            
                await sync_to_async(update_sold_ostatok_stock)(token, user_id, warehouse.sd_id, order_ids)
            
            shipping_db = await sync_to_async(ship_db_data)()
            _, report = await sync_to_async(ship_products)(shipping_db)
            
            print(report)

            try:
                await bot.send_message(GROUP_ID, report[:TELEGRAM_MESSAGE_LIMIT], parse_mode='HTML')
            except Exception as e:
                print(f"Error sending message: {e} in daily_shipping_report")


async def daily_redistribute_report():
    while True:
        await asyncio.sleep(DAILY_REDISTRIBUTE_REPORT)
            
        # redistribution_report = await sync_to_async(redistribute_products)()
        redistribute_db = await sync_to_async(redistribute_data)()
        
        _, redistribute_report = await sync_to_async(redistribute_products)(redistribute_db)
        try:
            if redistribute_report:
                await bot.send_message(GROUP_ID, redistribute_report[:TELEGRAM_MESSAGE_LIMIT])
            else:
                print("No redistribution report to send.")        
        except Exception as e:
            print(f"Error sending message: {e} in daily_redistribute_report")
            
            