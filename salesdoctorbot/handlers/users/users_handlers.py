from aiogram import types
from aiogram.dispatcher import FSMContext
from loader import dp
from data.config import CATEGORY_ID
from asgiref.sync import sync_to_async
from salesDoctorAuth import auth_sales_doctor
from django.core.exceptions import ObjectDoesNotExist
from utils.db_api.connector_db import get_warehouse_by_id, get_warehouse_by_name, get_warehouse_products, get_general_product
from salesdoctorbot.services import update_sold_ostatok_stock, getProducts_by_WH_Ca

MINIMUM_OSTATOK = 26
MAXIMUM_OSTATOK = 32
CONS_ADD = 6

@dp.message_handler(lambda message: message.get_command().startswith("/warehouse_"))
async def handle_warehouse_command(message: types.Message, state: FSMContext):
    command = message.get_command()
    print(command)
    warehouse_id = command.split("_")[1][0]

    try:
        warehouse = await get_warehouse_by_id(warehouse_id)
        general_warehouse = await get_warehouse_by_name("Основной склад")
        token, user_id = await sync_to_async(auth_sales_doctor)()
        
        if token and user_id:
            report = f"📊 <b>{warehouse.name} Omborining Hisoboti</b>"
            await sync_to_async(update_sold_ostatok_stock)(token, user_id, warehouse.sd_id, CATEGORY_ID)
            warehouse_products = await get_warehouse_products(warehouse=warehouse)

            for warehouse_product in warehouse_products:
                product_name = await sync_to_async(lambda: warehouse_product.product.name)()
                ostatok = warehouse_product.ostatok
                general_product = await get_general_product(product=warehouse_product.product, general_warehouse=general_warehouse)

                if ostatok <= MINIMUM_OSTATOK and general_product is not None and general_product.ostatok > 0:
                    missing_product = MAXIMUM_OSTATOK - ostatok
                    if missing_product - CONS_ADD < 0:
                        continue
                    round_product = round(missing_product / CONS_ADD)
                    quantity = round_product * CONS_ADD
                    if quantity >= general_product.ostatok:
                        quantity = general_product.ostatok
                        report += f"\n<b>{product_name}</b> | X{quantity} ta kerak, omborda ushbu mahsulot oxirgisi {general_product.ostatok} ta bor"
                        continue
                    elif quantity <= 0:
                        continue
                    else:
                        report += f"\n<b>{product_name}</b> | X{quantity} ta kerak! Omborda {general_product.ostatok} ta bor"
            
            await message.answer(report, parse_mode='HTML')
        else:
            await message.answer("Autentifikatsiya muvaffaqiyatsiz o'tdi")
    except ObjectDoesNotExist:
        await message.answer("Ombor topilmadi.")
