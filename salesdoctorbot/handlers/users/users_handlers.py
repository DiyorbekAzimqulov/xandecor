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
    await message.answer("Ushbu buyruqni ishlatish uchun sizda bunday ruxsat yo'q!")
    return