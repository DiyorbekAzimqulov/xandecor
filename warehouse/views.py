from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from salesdoctorbot.models import WareHouse, WareHouseProduct, StoreProduct, Store
from django.views import View
from django.db.models import Sum

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
        # Retrieve the specific warehouse, handle case if not found
        warehouse = get_object_or_404(WareHouse, pk=kwargs.get("id"))
        
        # Prepare data to be displayed
        data = []

        # Get all products for the current warehouse
        warehouse_products = WareHouseProduct.objects.filter(warehouse=warehouse, ostatok__gt=0, sold__gt=0)
        
        for wh_product in warehouse_products:
            product = wh_product.product
            ostatok = wh_product.ostatok

            # Get quantities of this product in each store
            store_products = StoreProduct.objects.filter(product=product, store__warehouse=warehouse)
            store_quantities = {store.name: store_products.filter(store=store).aggregate(quantity=Sum('quantity'))['quantity'] or 0
                                for store in Store.objects.filter(warehouse=warehouse)}
            
            # Calculate total quantity of the product in the warehouse
            left_product_count_in_warehouse = ostatok - sum(store_quantities.values())

            # Append data for this product
            data.append({
                'warehouse_name': warehouse.name,
                'product_name': product.name,
                'ostatok': ostatok,
                'store_quantities': store_quantities,
                'left_product_count_in_warehouse': left_product_count_in_warehouse
            })
        
        context = {
            'data': data,
            'warehouse': warehouse,  # Pass warehouse object to the template
        }
        return render(request, 'warehouse/wareHouse.html', context)



class StoreDetailView(View):
    def get(self, request, *args, **kwargs):
        store = get_object_or_404(Store, pk=kwargs.get("id"))
        context = {
            "store": store,
        }
        return render(request, "warehouse/store_detail.html", context)

