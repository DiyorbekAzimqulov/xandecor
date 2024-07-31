from django.urls import path
from .views import (
        WarehouseView, 
        WareHouseStoreView, 
        StoreDetailView, 
        edit_product_details, 
        get_stores, 
        discount_products,
        StoresView,
        StoreView,
        StoreWarehouseView,
        feedback
)

urlpatterns = [
    path("", WarehouseView.as_view(), name="warehouse_list"),
    path('<int:id>/', WareHouseStoreView.as_view(), name="wareHouse"),
    path('store/<int:id>/', StoreDetailView.as_view(), name='store_detail'),
    path('edit_product_details/', edit_product_details, name='edit_product_details'),
    path('get_stores/', get_stores, name='get_stores'),
    path('discount-products-list/', discount_products, name='discount_products_list'),
    # stores
    path('stores/', StoresView.as_view(), name='stores'),
    path('main_store/<int:id>/', StoreView.as_view(), name='main_store'),
    path('warehouse_store/<int:id>/', StoreWarehouseView.as_view(), name='warehouse_store'),
    path('feedback/', feedback, name='feedback'),
]
