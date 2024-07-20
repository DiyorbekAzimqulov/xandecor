import asyncio
from asgiref.sync import sync_to_async
from salesdoctorbot.loader import bot
from salesdoctorbot.models import WareHouse, WareHouseProduct
from salesdoctorbot.salesDoctorAuth import auth_sales_doctor
from salesdoctorbot.services import getProducts_by_WH_Ca, update_sold_ostatok_stock
from salesdoctorbot.data.config import CATEGORY_ID, GROUP_ID
from salesdoctorbot.reports_db import (
    ship_db_data, ship_products, 
    redistribute_products, 
    redistribute_data, 
    find_forgotten_shipments, 
    generate_forgotten_shipment_report
)
from orm_app.models import Product, DiscountEvent, TelegramGroup

# Constants for the daily report tasks hour in seconds since the start of the day
DAILY_SHIPPING_HOUR = 7 * 60 * 60  # 7:00 AM
DAILY_REDISTRIBUTE_HOUR = DAILY_SHIPPING_HOUR + 10 * 60  # 7:10 AM
DAILY_FORGOTTEN_SHIPMENTS_HOUR = DAILY_REDISTRIBUTE_HOUR + 10 * 60  # 7:20 AM

# DAILY_SHIPPING_HOUR = 5  # 7:00 AM
# DAILY_REDISTRIBUTE_HOUR = DAILY_SHIPPING_HOUR + 1  # 7:10 AM
# DAILY_FORGOTTEN_SHIPMENTS_HOUR = DAILY_REDISTRIBUTE_HOUR + 1  # 7:20 AM


TELEGRAM_MESSAGE_LIMIT = 4096  # Telegram message character limit



async def daily_shipping_report() -> str:
    while True:
        print("Daily shipping report task starting...")
        # Calculate the time until the next report
        await asyncio.sleep(DAILY_SHIPPING_HOUR)
        
        token, user_id = await sync_to_async(auth_sales_doctor)()
        if token and user_id:
            await sync_to_async(getProducts_by_WH_Ca)(token, user_id, CATEGORY_ID)
            
            # All other warehouses
            warehouses = await sync_to_async(lambda: list(WareHouse.objects.all()))()
            for warehouse in warehouses:
                order_ids = await sync_to_async(lambda: list(WareHouseProduct.objects.filter(warehouse=warehouse).values_list('product__sd_id', flat=True)))()            
                print("Updating Products ...")
                await sync_to_async(update_sold_ostatok_stock)(token, user_id, warehouse.sd_id, order_ids)
                print("Products Updated")
                
            
            shipping_db = await sync_to_async(ship_db_data)()
            _, report = await sync_to_async(ship_products)(shipping_db)
            
            print(report)

            try:
                await bot.send_message(GROUP_ID, report[:TELEGRAM_MESSAGE_LIMIT], parse_mode='HTML')
            except Exception as e:
                print(f"Error sending message: {e} in daily_shipping_report")


async def daily_redistribute_report():
    while True:
        print("Daily redistribute report task starting...")
        # Calculate the time until the next report
        await asyncio.sleep(DAILY_REDISTRIBUTE_HOUR)
            
        redistribute_db = await sync_to_async(redistribute_data)()
        
        _, redistribute_report = await sync_to_async(redistribute_products)(redistribute_db)
        try:
            if redistribute_report:
                await bot.send_message(GROUP_ID, redistribute_report[:TELEGRAM_MESSAGE_LIMIT])
            else:
                print("No redistribution report to send.")        
        except Exception as e:
            print(f"Error sending message: {e} in daily_redistribute_report")
            

async def daily_forgotten_shipments():
    while True:
        print("Daily forgotten shipments task starting...")
        # Calculate the time until the next report
        await asyncio.sleep(DAILY_FORGOTTEN_SHIPMENTS_HOUR)
        
        forgotten_shipments = await sync_to_async(find_forgotten_shipments)()
        report = await sync_to_async(generate_forgotten_shipment_report)(forgotten_shipments)
        
        try:
            if report:
                await bot.send_message(GROUP_ID, report[:TELEGRAM_MESSAGE_LIMIT])
            else:
                print("No forgotten shipments report to send.")
        except Exception as e:
            print(f"Error sending message: {e} in daily_forgotten_shipments")


# async def daily_discount_report():
#     while True:
#         print("Daily discount report task starting...")
#         # Calculate the time until the next report
#         await asyncio.sleep(