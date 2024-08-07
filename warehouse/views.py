import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from salesdoctorbot.models import Client, Feedback, StockProduct, WareHouse, WareHouseProduct, StoreProduct, Store
from django.views import View
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from orm_app.models import DiscountEvent
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.contrib import messages 


class SuperuserRequiredMixin(AccessMixin):
    """Ensure that the current user is authenticated and is a superuser."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

class WarehouseView(SuperuserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        warehouses = WareHouse.objects.all().exclude(name="Основной склад")
        context = {
            'warehouses': warehouses,
            'active_page': 'warehouse_page'
        }
        return render(request, "general/warehouse_list.html", context)

class WareHouseStoreView(View):
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('prompt', '')
        is_from_all = request.GET.get('isFromAll') == 'True'
        last_warehouse_uuid = request.GET.get('last_warehouse_uuid', '')
        
        data = []
        stores = []
        warehouses = WareHouse.objects.all() if is_from_all else [get_object_or_404(WareHouse, uuid=kwargs.get("uuid") or last_warehouse_uuid)]
        
        for warehouse in warehouses:
            warehouse_products = WareHouseProduct.objects.filter(
                warehouse=warehouse,
                product__name__icontains=search_query,
                # ostatok__gt=0,
                # sold__gt=0
            )
            for wh_product in warehouse_products:
                product = wh_product.product
                ostatok = wh_product.ostatok
                shelf = wh_product.shelf
                store_products = StoreProduct.objects.filter(
                    product=product,
                    store__warehouse=warehouse
                )
                store_quantities = {
                    store.name: store_products.filter(store=store).aggregate(quantity=Sum('quantity'))['quantity'] or 0
                    for store in Store.objects.filter(warehouse=warehouse)
                }
                
                left_product_count_in_warehouse = ostatok - sum(store_quantities.values())
                
                data.append({
                    'warehouse_name': warehouse.name,
                    'product_name': product.name,
                    'ostatok': ostatok,
                    'store_quantities': store_quantities,
                    'left_product_count_in_warehouse': left_product_count_in_warehouse,
                    'shelf': shelf,
                    'product_id': product.id
                })
                stores = Store.objects.filter(warehouse=warehouse)
        
        context = {
            'stores': stores,
            'data': data,
            'warehouse': warehouses[0] if not is_from_all else None,
            'active_page': 'wareHouse',
            'search_query': search_query,
            'is_from_all': is_from_all,
            'last_warehouse_uuid': warehouses[0].uuid if not is_from_all else last_warehouse_uuid
        }
        return render(request, 'warehouse/wareHouse.html', context)


@csrf_exempt
def update_store_quantities(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        warehouse_id = request.POST.get('warehouse_id')
        quantities = json.loads(request.POST.get('quantities', '{}'))
        try:
            warehouse = WareHouse.objects.get(id=warehouse_id)
        except WareHouse.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Warehouse not found.'}, status=404)

        for store_name, quantity in quantities.items():
            try:
                store = Store.objects.get(name=store_name, warehouse=warehouse)
                store_product, created = StoreProduct.objects.get_or_create(
                    store=store, product_id=product_id
                )
                store_product.quantity = quantity
                store_product.save()
            except Store.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': f'Store "{store_name}" not found.'}, status=404)

        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)



class StoreDetailView(View):
    def get(self, request, *args, **kwargs):
        store = get_object_or_404(Store, uuid=kwargs.get("uuid"))
        store_products = StoreProduct.objects.filter(store=store, quantity__gt=0)
        context = {
            "store": store,
            "store_products": store_products
        }
        return render(request, "warehouse/store_detail.html", context)
    

def discount_products(request):
    events = DiscountEvent.objects.all().prefetch_related("products")
    context = {
        'events': events,
        'active_page': 'discount_products_list'
    }
    return render(request, 'warehouse/discounts.html', context)


""" Stores part """


class StoresView(SuperuserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        warehouses = WareHouse.objects.all().exclude(name="Основной склад")
        stores_dict = {}

        for warehouse in warehouses:
            stores_dict[warehouse.name] = Store.objects.filter(warehouse=warehouse)
            
        context = {
            'stores_dict': stores_dict,
            'active_page': 'stores_page'
        }
        return render(request, "store/stores.html", context=context)


class StoreView(View):  
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('prompt', '')
        
        store = get_object_or_404(Store, uuid=kwargs.get("uuid"))
        store_products = StoreProduct.objects.filter(store=store, quantity__gt=0)
        warehouse = store.warehouse
        if search_query:
            store_products = store_products.filter(product__name__icontains=search_query)

        context = {
            "warehouse": warehouse,
            "store": store,
            "store_products": store_products
        }
        return render(request, "store/Store.html", context)
    
class StoreWarehouseView(View):
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('name', '')
        store = get_object_or_404(Store, uuid=kwargs.get("uuid"))
        warehouse = store.warehouse
        
        # Retrieve all warehouse products
        warehouse_products = WareHouseProduct.objects.filter(warehouse=warehouse)
        # Retrieve all store products
        store_products = StoreProduct.objects.filter(store=store)
        
        # Create a dictionary for easy lookup of products by name
        product_dict = {}
        for wp in warehouse_products:
            product_dict[wp.product.name] = {"warehouse_quantity": wp.ostatok, "store_quantity": 0}
        for sp in store_products:
            if sp.product.name in product_dict:
                product_dict[sp.product.name]["store_quantity"] = sp.quantity
            else:
                product_dict[sp.product.name] = {"warehouse_quantity": 0, "store_quantity": sp.quantity}

        # If a search query is present, filter products
        if search_query:
            product_dict = {name: data for name, data in product_dict.items() if search_query.lower() in name.lower()}

        # Convert the dictionary back to a list for the template
        products = [
            {"name": name, "warehouse_quantity": data["warehouse_quantity"], "store_quantity": data["store_quantity"]}
            for name, data in product_dict.items()
        ]
        
        context = {
            "store": store,
            "warehouse": warehouse,
            "products": products,
            "search_query": search_query,  # Pass the search query back to the template
        }
        
        return render(request, 'store/store_warehouse.html', context)


class FeedbackView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        feedback = request.POST.get('feedback')
        store_uuid = request.POST.get('store_uuid')
        from_who = request.POST.get('from_who')
        if from_who == 'store':
            from_who = True
        else:
            from_who = False
        store = get_object_or_404(Store, uuid=store_uuid)
        warehouse = store.warehouse
        feedback = Feedback.objects.create(store=store, warehouse=warehouse, text=feedback, is_store=from_who)
        
        try:
            # Process feedback here (e.g., save to database)
            messages.success(request, 'Xabar muvaffaqiyatli yuborildi.')
        except Exception as e:
            messages.error(request, 'Xatolik yuz berdi. Iltimos, qayta urinib ko\'ring.')
        
        return redirect(reverse('main_store', kwargs={'uuid': store_uuid}))
    
class ClientView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'check_client':
                return self.check_client(request)
            elif action == 'update_client_enrollment':
                return self.update_client_enrollment(request)
            elif action == 'create_client':
                return self.create_client(request)
        return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

    def check_client(self, request):
        phone = request.POST.get('phone')
        exists = Client.objects.filter(phone=phone).exists()
        return JsonResponse({'exists': exists})

    def update_client_enrollment(self, request):
        phone = request.POST.get('phone')
        try:
            client = Client.objects.get(phone=phone)
            client.enrollement_count += 1
            client.save()
            return JsonResponse({'status': 'success'})
        except Client.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Client not found'}, status=404)

    def create_client(self, request):
        warehouse_id = request.POST.get('warehouse_id')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        
        warehouse = get_object_or_404(WareHouse, id=warehouse_id)
        
        Client.objects.create(name=name, phone=phone, warehouse=warehouse)
        return JsonResponse({'status': 'success'})
