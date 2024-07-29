from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from salesdoctorbot.models import StockProduct, WareHouse, WareHouseProduct, StoreProduct, Store
from django.views import View
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from orm_app.models import DiscountEvent

class SuperuserRequiredMixin(AccessMixin):
    """Ensure that the current user is authenticated and is a superuser."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

class WarehouseView(SuperuserRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        warehouses = WareHouse.objects.all().exclude(name="Основной склад")
        return render(request, "general/warehouse_list.html", {"warehouses": warehouses})

class WareHouseStoreView(View):
    def get(self, request, *args, **kwargs):
        search_query = request.GET.get('prompt', '')
        is_from_all = request.GET.get('isFromAll') == 'True'  # Check if the checkbox is selected

        # Prepare data to be displayed
        data = []
        warehouse = None

        if is_from_all:
            # Search across all warehouses
            warehouse_products = WareHouseProduct.objects.filter(
                product__name__icontains=search_query, 
                ostatok__gt=0, 
                sold__gt=0
            )
            warehouses = WareHouse.objects.all()
        else:
            # Retrieve the specific warehouse
            warehouse = get_object_or_404(WareHouse, pk=kwargs.get("id"))
            warehouse_products = WareHouseProduct.objects.filter(
                warehouse=warehouse, 
                product__name__icontains=search_query, 
                ostatok__gt=0, 
                sold__gt=0
            )
            warehouses = [warehouse]
        
        for wh_product in warehouse_products:
            product = wh_product.product
            ostatok = wh_product.ostatok
            shelf = wh_product.shelf

            for warehouse in warehouses:
                store_products = StoreProduct.objects.filter(
                    product=product, 
                    store__warehouse=warehouse
                )
                store_quantities = {
                    store.name: store_products.filter(store=store).aggregate(quantity=Sum('quantity'))['quantity'] or 0
                    for store in Store.objects.filter(warehouse=warehouse)
                }
                
                stores = Store.objects.filter(warehouse=warehouse)

                left_product_count_in_warehouse = ostatok - sum(store_quantities.values())

                data.append({
                    'warehouse_name': warehouse.name,
                    'product_name': product.name,
                    'ostatok': ostatok,
                    'store_quantities': store_quantities,
                    'left_product_count_in_warehouse': left_product_count_in_warehouse,
                    'shelf': shelf,
                    'product_id': product.id  # Assuming the product has an ID field
                })
        
        context = {
            'stores': stores,
            'data': data,
            'warehouse': warehouse if not is_from_all else None,  # Pass warehouse object if not searching all
            'active_page': 'wareHouse',
            'search_query': search_query,
            'is_from_all': is_from_all
        }
        return render(request, 'warehouse/wareHouse.html', context)


class StoreDetailView(View):
    def get(self, request, *args, **kwargs):
        store = get_object_or_404(Store, pk=kwargs.get("id"))
        store_products = StoreProduct.objects.filter(store=store, quantity__gt=0)
        context = {
            "store": store,
            "store_products": store_products
        }
        return render(request, "warehouse/store_detail.html", context)
    
    
@csrf_exempt
def edit_product_details(request):
    warehouse_id = request.POST.get('warehouse_id')
    product_id = request.POST.get('product_id')
    store_id = request.POST.get('store_id')
    new_shelf = request.POST.get('shelf')
    new_quantity = request.POST.get('quantity')

    if not all([warehouse_id, product_id, store_id, new_shelf, new_quantity]):
        return JsonResponse({'success': False, 'error': 'Missing data'})

    print(warehouse_id, product_id, store_id, new_shelf, new_quantity)
    
    try:
        warehouse = WareHouse.objects.get(id=warehouse_id)
        print(warehouse)
        product = StockProduct.objects.get(id=product_id)
        print(product)
        warehouse_product = WareHouseProduct.objects.get(warehouse=warehouse, product=product)
        print(warehouse_product)
        store = Store.objects.get(id=store_id)
        print(store)
        store_product = StoreProduct.objects.get(store=store, product_id=product_id)
        print(store_product)
        warehouse_product.shelf = new_shelf
        print(warehouse_product.shelf)
        store_product.quantity = new_quantity
        print(store_product.quantity)
        warehouse_product.save()
        store_product.save()
        

        return JsonResponse({'success': True})
    except StoreProduct.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Store product not found'})
    except WareHouseProduct.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Warehouse product not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def get_stores(request):
    stores = Store.objects.all()
    store_list = list(stores.values('id', 'name'))
    return JsonResponse({'stores': store_list}) 




def discount_products(request):
    events = DiscountEvent.objects.all().prefetch_related("products")
    context = {
        'events': events,
        'active_page': 'discount_products_list'
    }
    return render(request, 'warehouse/discounts.html', context)