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
        is_from_all = request.GET.get('isFromAll') == 'True'

        warehouse_products = []
        if is_from_all:
            warehouse_products = WareHouseProduct.objects.filter(
                product__name__icontains=search_query,
                ostatok__gt=0,
                sold__gt=0
            )
        else:
            warehouse = get_object_or_404(WareHouse, pk=kwargs.get("id"))
            warehouse_products = WareHouseProduct.objects.filter(
                warehouse=warehouse,
                product__name__icontains=search_query,
                ostatok__gt=0,
                sold__gt=0
            )

        stores = Store.objects.all()
        context = {
            'warehouse_products': warehouse_products,
            'stores': stores,
            'search_query': search_query,
            'is_from_all': is_from_all
        }
        return render(request, 'warehouse/wareHouse.html', context)

class StoreDetailView(View):
    def get(self, request, *args, **kwargs):
        store = get_object_or_404(Store, pk=kwargs.get("id"))
        store_products = StoreProduct.objects.filter(store=store)

        context = {
            "store": store,
            "store_products": store_products,
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
        product = StockProduct.objects.get(id=product_id)
        warehouse_product = WareHouseProduct.objects.get(warehouse=warehouse, product=product)
        store = Store.objects.get(id=store_id)
        store_product = StoreProduct.objects.get(store=store, product_id=product_id)
        warehouse_product.shelf = new_shelf
        store_product.quantity = new_quantity
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
