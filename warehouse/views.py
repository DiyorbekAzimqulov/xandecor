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
        context = {
            'warehouses': warehouses,
            'active_page': 'warehouse_page'
        }
        return render(request, "general/warehouse_list.html", context)

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
            warehouse = get_object_or_404(WareHouse, uuid=kwargs.get("uuid"))
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
    
import logging
logger = logging.getLogger(__name__)

@csrf_exempt
def edit_product_details(request):
    warehouse_id = request.POST.get('warehouse_id')
    product_id = request.POST.get('product_id')
    store_id = request.POST.get('store_id')
    new_shelf = request.POST.get('shelf')
    new_quantity = request.POST.get('quantity')

    logger.info(f"Received request with warehouse_id={warehouse_id}, product_id={product_id}, store_id={store_id}, new_shelf={new_shelf}, new_quantity={new_quantity}")

    if not all([warehouse_id, product_id, store_id, new_shelf, new_quantity]):
        return JsonResponse({'success': False, 'error': 'Missing data'})

    try:
        new_quantity = int(new_quantity)
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid quantity'})

    try:
        warehouse = WareHouse.objects.get(id=warehouse_id)
        product = StockProduct.objects.get(id=product_id)
        warehouse_product = WareHouseProduct.objects.get(warehouse=warehouse, product=product)
        store = Store.objects.get(id=store_id)

        # Ensure we are unpacking the tuple correctly
        store_product, created = StoreProduct.objects.get_or_create(store=store, product=product, defaults={'quantity': 0})

        # Update the fields
        warehouse_product.shelf = new_shelf
        store_product.quantity = new_quantity

        # Save changes
        warehouse_product.save()
        store_product.save()

        return JsonResponse({'success': True})
    except WareHouse.DoesNotExist:
        logger.error(f"Warehouse with id {warehouse_id} not found")
        return JsonResponse({'success': False, 'error': 'Warehouse not found'})
    except StockProduct.DoesNotExist:
        logger.error(f"Product with id {product_id} not found")
        return JsonResponse({'success': False, 'error': 'Product not found'})
    except WareHouseProduct.DoesNotExist:
        logger.error(f"Warehouse product not found for warehouse {warehouse_id} and product {product_id}")
        return JsonResponse({'success': False, 'error': 'Warehouse product not found'})
    except Store.DoesNotExist:
        logger.error(f"Store with id {store_id} not found")
        return JsonResponse({'success': False, 'error': 'Store not found'})
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Error updating product details'})


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


def feedback(request):
    return render(request, 'feedback.html')