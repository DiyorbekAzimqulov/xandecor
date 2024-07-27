from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from salesdoctorbot.models import WareHouse, WareHouseProduct, StoreProduct, Store
from django.views import View
from django.db.models import Sum
from django.http import JsonResponse

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
        context = {
            "store": store,
        }
        return render(request, "warehouse/store_detail.html", context)

def edit_shelf(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        new_shelf = request.POST.get('shelf')

        try:
            warehouse_product = WareHouseProduct.objects.get(product_id=product_id)
            warehouse_product.shelf = new_shelf
            warehouse_product.save()
            return JsonResponse({'success': True})
        except WareHouseProduct.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})
