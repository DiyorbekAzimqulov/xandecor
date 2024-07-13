from django.shortcuts import render
from salesdoctorbot.salesDoctorAuth import auth_sales_doctor
from salesdoctorbot.models import WareHouse, StockProduct, WareHouseProduct
from salesdoctorbot.services import getProducts_by_WH_Ca
from django.template.loader import render_to_string
from django.http import JsonResponse

NAME_CATEGORY = "Xan Decor Naxt"
CATEGORY_ID = "d0_5"

def sales_doctor(request):
    token, user_id = auth_sales_doctor()
    context = {"status": False, "error": "Authentication failed"}

    if token and user_id:
        stockproducts = WareHouseProduct.objects.filter(
            category__sd_id=CATEGORY_ID,
            ostatok__gt=0
        ).distinct()

        warehouse_names = list(WareHouse.objects.values_list('name', flat=True))

        # Ensure 'Основной склад' is first in the list
        if "Основной склад" in warehouse_names:
            warehouse_names.remove("Основной склад")
            warehouse_names.insert(0, "Основной склад")

        product_data = {}
        for product in stockproducts:
            if product.product.name not in product_data:
                product_data[product.product.name] = {
                    'total_prixod': 0,
                    'total_sold': 0,
                    'total_ostatok': 0,
                    'stores': {}
                }
            product_data[product.product.name]['total_prixod'] += product.prixod
            product_data[product.product.name]['total_sold'] += product.sold
            product_data[product.product.name]['total_ostatok'] += product.ostatok
            product_data[product.product.name]['stores'][product.warehouse.name] = {
                'prixod': product.prixod,
                'sold': product.sold,
                'ostatok': product.ostatok
            }

        context = {
            "status": True,
            "warehouse_names": warehouse_names,
            "product_data": product_data,
        }

    return render(request, "sales_doctor.html", context)


def fetch_warehouse_data(request):
    warehouse = request.GET.get('warehouse')
    
    stockproducts = WareHouseProduct.objects.filter(
        category__sd_id=CATEGORY_ID,
        warehouse__name=warehouse,
        ostatok__gt=0
    ).distinct()

    product_data = {}
    for product in stockproducts:
        if product.product.name not in product_data:
            product_data[product.product.name] = {
                'total_prixod': 0,
                'total_sold': 0,
                'total_ostatok': 0,
                'stores': {}
            }
        product_data[product.product.name]['total_prixod'] += product.prixod
        product_data[product.product.name]['total_sold'] += product.sold
        product_data[product.product.name]['total_ostatok'] += product.ostatok
        product_data[product.product.name]['stores'][product.warehouse.name] = {
            'prixod': product.prixod,
            'sold': product.sold,
            'ostatok': product.ostatok
        }

    table_body_html = render_to_string('product_zapravka.html', {
        'product_data': product_data,
        'warehouse_names': [warehouse],
    })
    
    return JsonResponse({'html': table_body_html})