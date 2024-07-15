import asyncio
from asgiref.sync import sync_to_async
from salesdoctorbot.loader import bot
from salesdoctorbot.models import WareHouse, WareHouseProduct
from salesdoctorbot.salesDoctorAuth import auth_sales_doctor
from salesdoctorbot.services import getProducts_by_WH_Ca, update_sold_ostatok_stock
from salesdoctorbot.data.config import CATEGORY_ID, GROUP_ID
from salesdoctorbot.reports_db import ship_db_data, ship_products, redistribute_products, redistribute_data, find_forgotten_shipments, generate_forgotten_shipment_report
from django.utils.timezone import now
import datetime

DAILY_SHIPPING_HOUR, DAILY_SHIPPING_MINUTE = 12, 20
DAILY_REDISTRIBUTE_HOUR, DAILY_REDISTRIBUTE_MINUTE = 7, 5
DAILY_FORGOTTEN_SHIPMENTS_HOUR, DAILY_FORGOTTEN_SHIPMENTS_MINUTE = 7, 10

TELEGRAM_MESSAGE_LIMIT = 4096  # Telegram message character limit

async def calculate_seconds_until_next_report(hour: int, minute: int) -> int:
    """Calculate the seconds until the next occurrence of the specified hour and minute."""
    current_time = now()
    report_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if current_time >= report_time:
        report_time += datetime.timedelta(days=1)
    return (report_time - current_time).total_seconds()

async def daily_shipping_report() -> str:
    while True:
        # Calculate the time until the next report
        seconds_until_next_report = await calculate_seconds_until_next_report(DAILY_SHIPPING_HOUR, DAILY_SHIPPING_MINUTE)
        await asyncio.sleep(seconds_until_next_report)
        
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
        # Calculate the time until the next report
        seconds_until_next_report = await calculate_seconds_until_next_report(DAILY_REDISTRIBUTE_HOUR, DAILY_REDISTRIBUTE_MINUTE)
        await asyncio.sleep(seconds_until_next_report)
            
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
        # Calculate the time until the next report
        seconds_until_next_report = await calculate_seconds_until_next_report(DAILY_FORGOTTEN_SHIPMENTS_HOUR, DAILY_FORGOTTEN_SHIPMENTS_MINUTE)
        await asyncio.sleep(seconds_until_next_report)
        
        forgotten_shipments = await sync_to_async(find_forgotten_shipments)()
        report = await sync_to_async(generate_forgotten_shipment_report)(forgotten_shipments)
        
        try:
            if report:
                await bot.send_message(GROUP_ID, report[:TELEGRAM_MESSAGE_LIMIT])
            else:
                print("No forgotten shipments report to send.")
        except Exception as e:
            print(f"Error sending message: {e} in daily_forgotten_shipments")
