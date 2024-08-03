from django.shortcuts import render
from salesdoctorbot.salesDoctorAuth import auth_sales_doctor
from salesdoctorbot.models import WareHouse, WareHouseProduct
from orm_app.models import Product, DiscountEvent, TelegramGroup
from django.contrib.auth.mixins import AccessMixin
from django.views import View
from salesdoctorbot.report_functions import (
    ship_db_data, 
    ship_products,
    redistribute_data,
    redistribute_products,
    find_forgotten_shipments
)
from django.shortcuts import redirect
from django.http import HttpResponse



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
        search_query = request.GET.get('name', '')
        context = {"status": False, "error": "Authentication failed"}

        # Fetch products with positive 'prixod' and 'ostatok' and filter by category
        warehouse_products = WareHouseProduct.objects.select_related('product', 'warehouse').filter(
            category__sd_id=CATEGORY_ID,
            prixod__gt=0,
            ostatok__gt=0
        ).distinct().order_by('product__name')

        # Filter by search query if present
        if search_query:
            warehouse_products = warehouse_products.filter(product__name__icontains=search_query)

        # Get all warehouse names
        warehouse_names = list(WareHouse.objects.values_list('name', flat=True))

        # Ensure 'Основной склад' is first in the list
        if "Основной склад" in warehouse_names:
            warehouse_names.remove("Основной склад")
            warehouse_names.insert(0, "Основной склад")

        # Prepare product data for rendering
        product_data = {}
        for warehouse_product in warehouse_products:
            product_name = warehouse_product.product.name
            if product_name not in product_data:
                product_data[product_name] = {
                    'total_prixod': 0,
                    'total_sold': 0,
                    'total_ostatok': 0,
                    'stores': {}
                }
            product_data[product_name]['total_prixod'] += warehouse_product.prixod
            product_data[product_name]['total_sold'] += warehouse_product.sold
            product_data[product_name]['total_ostatok'] += warehouse_product.ostatok
            product_data[product_name]['stores'][warehouse_product.warehouse.name] = {
                'prixod': warehouse_product.prixod,
                'sold': warehouse_product.sold,
                'ostatok': warehouse_product.ostatok
            }

        context = {
            "status": True,
            "warehouse_names": warehouse_names,
            "product_data": product_data,
            "active_page": 'sales_doctor',
            'search_query': search_query
        }

        return render(request, self.template_name, context)

class ShipProductView(SuperuserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('name', '')
        ship_data = ship_db_data()
        data, _ = ship_products(ship_data)
        
        # Filter data based on search query
        if search_query:
            filtered_data = {}
            for ware, prods in data.items():
                filtered_products = [prod for prod in prods if search_query.lower() in prod.get('product_name', '').lower()]
                if filtered_products:
                    filtered_data[ware] = filtered_products
            data = filtered_data

        # Calculate max_length only if data is not empty
        if data:
            max_length = max(len(products) for products in data.values())
        else:
            max_length = 0

        # Create a list of indices
        indices = list(range(max_length))

        context = {
            'data': data,
            'active_page': 'ship_product',
            'indices': indices,
            'search_query': search_query
        }

        return render(request, "general/ship_products.html", context)
        
class RedistributeProductView(SuperuserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('name', '')
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
            
            # Filter by search query
            if search_query.lower() in product_name.lower():
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
            'search_query': search_query
        }

        return render(request, "general/redistribute_products.html", context)

class ForgottenShipment(SuperuserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('name', '')
        forgotten_product = find_forgotten_shipments()
        
        products_dic = {}
        for product in forgotten_product:
            if search_query.lower() in product.product.name.lower():
                products_dic[product.product.name] = {
                    "prxod": product.prixod,
                    "sold": product.sold,
                    "ostatok": product.ostatok
                }
        
        context = {
            'data': products_dic,
            'search_query': search_query,
            'active_page': 'forgotten_product'
        }

        return render(request, "general/forgotten_product.html", context)


class DiscountProductView(SuperuserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        products = Product.objects.all().order_by('name')
        groups = TelegramGroup.objects.all()
        events = DiscountEvent.objects.all().order_by('-created_at')
        context = {
            "products": products, 
            "groups": groups, 
            "events": events
            }
        return render(request, "general/discount_products.html", context)

    def post(self, request, *args, **kwargs):
        selected_products = request.POST.getlist('products')
        discount_number = request.POST.get('discount_number')
        selected_groups = request.POST.getlist('groups')
        
        if selected_products and discount_number and selected_groups:
            event = DiscountEvent(discount=discount_number)
            event.save()
            event.products.set(selected_products)
            event.group.set(selected_groups)
            event.save()
        return redirect('discount_product')


class RemoveDiscountEventView(View):
    def post(self, request, event_id, *args, **kwargs):
        try:
            event = DiscountEvent.objects.get(id=event_id)
            event.delete()
            return redirect('discount_product')
        except DiscountEvent.DoesNotExist:
            # Handle the case where the event does not exist
            return redirect('discount_product')
