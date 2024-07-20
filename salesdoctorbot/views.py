from django.shortcuts import render
from salesdoctorbot.salesDoctorAuth import auth_sales_doctor
from salesdoctorbot.models import WareHouse, WareHouseProduct
from django.contrib.auth.mixins import AccessMixin
from django.views import View
from salesdoctorbot.reports_db import (
    ship_db_data, 
    ship_products,
    redistribute_data,
    redistribute_products,
    find_forgotten_shipments
)

NAME_CATEGORY = "Xan Decor Naxt"
CATEGORY_ID = "d0_5"

class SuperuserRequiredMixin(AccessMixin):
    """Ensure that the current user is authenticated and is a superuser."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

class SalesDoctorView(SuperuserRequiredMixin, View):
    template_name = "general/sales_doctor.html"
    
    def get(self, request, *args, **kwargs):
        token, user_id = auth_sales_doctor()
        context = {"status": False, "error": "Authentication failed"}

        if token and user_id:
            stockproducts = WareHouseProduct.objects.filter(
                category__sd_id=CATEGORY_ID,
                ostatok__gt=0
            ).distinct().order_by('product__name')  # Sort by product name

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
                "active_page": 'sales_doctor'
            }

        return render(request, self.template_name, context)


class ShipProductView(SuperuserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        ship_data = ship_db_data()
        data, _ = ship_products(ship_data)

        max_length = max(len(products) for products in data.values())

        # Create a list of indices
        indices = list(range(max_length))

        context = {
            'data': data,
            'active_page': 'ship_product',
            'indices': indices
        }


        return render(request, "general/ship_products.html", context)

class RedistributeProductView(SuperuserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        data_dic = redistribute_data()
        data, _ = redistribute_products(data_dic)
        
        # Fetch all warehouse names
        all_warehouses = list(WareHouse.objects.values_list('name', flat=True))
        
        # Create a mapping dictionary
        mapping_dic = {}
        for location_name, units in data.items():
            warehouse_name = location_name[1]
            subwarehouse = location_name[2]
            product_name = location_name[0]
            if warehouse_name not in mapping_dic:
                mapping_dic[warehouse_name] = []
            mapping_dic[warehouse_name].append({
                "units": units,
                "subwarehouse": subwarehouse,
                "product_name": product_name
            })

        # Sort the mapping dictionary by warehouse names
        sorted_mapping = {k: mapping_dic[k] for k in sorted(mapping_dic.keys(), key=lambda x: (all_warehouses.index(x) if x in all_warehouses else float('inf'), x))}

        context = {
            'data': sorted_mapping,
            'active_page': 'redistribute_product',
        }

        return render(request, "general/redistribute_products.html", context)


class ForgottenShipment(SuperuserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        forgotten_product = find_forgotten_shipments()
        products_dic = {}
        for product in forgotten_product:
            products_dic[product.product.name] = {
                    "prxod": product.prixod,
                    "sold": product.sold,
                    "ostatok": product.ostatok
                    }
                
        context = {
            'data': products_dic,
            'active_page': 'forgotten_product'
        }

        return render(request, "general/forgotten_product.html", context)
