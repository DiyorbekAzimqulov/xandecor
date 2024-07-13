import os
import sys

from django.utils import timezone

# Ensure the parent directory of 'orm' is in the PYTHONPATH
sys.path.append('/app')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orm.settings")
from django import setup

setup()
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from salesdoctorbot.models import WareHouse, StockProduct, WareHouseProduct
from salesdoctorbot.services import getProducts_by_WH_Ca, update_sold_ostatok_stock
from salesdoctorbot.salesDoctorAuth import auth_sales_doctor
from django.db.models import Q


@sync_to_async
def get_general_warehouse():
    return WareHouse.objects.get(name="Основной склад")

@sync_to_async
def get_warehouses():
    return WareHouse.objects.exclude(name="Основной склад").values_list()

@sync_to_async
def get_stock_products_by_warehouse(warehouse):
    return StockProduct.objects.filter(warehouseproduct__warehouse=warehouse)

@sync_to_async
def get_none_zero_warehouse_products(warehouse):
    return WareHouseProduct.objects.filter(warehouse=warehouse, prixod__gt=0)

@sync_to_async
def get_filtered_warehouse_products(warehouse, product):
    return WareHouseProduct.objects.filter(warehouse=warehouse, product=product).first()

@sync_to_async
def async_getProducts_by_WH_Ca(token, user_id, category_id):
    return getProducts_by_WH_Ca(token, user_id, category_id)

@sync_to_async
def async_auth_sales_doctor():
    return auth_sales_doctor()

@sync_to_async
def async_update_sold_ostatok_stock(token, user_id, warehouse_id, order_ids):
    return update_sold_ostatok_stock(token, user_id, warehouse_id, order_ids)

@sync_to_async
def get_warehouse_products(warehouse, general_warehouse, product):
    return WareHouseProduct.objects.filter(
        ~Q(warehouse=warehouse) & ~Q(warehouse=general_warehouse),
        product=product
    ).order_by('-ostatok')
    
@sync_to_async
def get_warehouse_by_id(warehouse_id):
    return WareHouse.objects.get(id=warehouse_id)

@sync_to_async
def get_warehouse_by_name(name):
    return WareHouse.objects.get(name=name)

@sync_to_async
def get_warehouse_products(warehouse):
    return list(WareHouseProduct.objects.filter(warehouse=warehouse))

@sync_to_async
def get_general_product(product, general_warehouse):
    return WareHouseProduct.objects.filter(product=product, warehouse=general_warehouse).first()
