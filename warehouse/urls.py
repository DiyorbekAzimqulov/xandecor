from django.urls import path
from .views import (
    WarehouseView,
    WareHouseStoreView,
    StoreDetailView,
    discount_products,
    StoresView,
    StoreView,
    StoreWarehouseView,
    FeedbackView,
    update_store_quantities,
    ClientView
)

urlpatterns = [
    path("", WarehouseView.as_view(), name="warehouse_list"),
    path('warehouse_stores/', StoresView.as_view(), name='warehouse_stores'),
    path('<uuid:uuid>/', WareHouseStoreView.as_view(), name="wareHouse"),
    path('warehouse/all/', WareHouseStoreView.as_view(), name='wareHouse_all'),
    path('update-store-quantities/', update_store_quantities, name='update_store_quantities'),
    path('store/<uuid:uuid>/', StoreDetailView.as_view(), name='store_detail'),
    path('discount-products-list/', discount_products, name='discount_products_list'),
    path('main_store/<uuid:uuid>/', StoreView.as_view(), name='main_store'),
    path('warehouse_store/<uuid:uuid>/', StoreWarehouseView.as_view(), name='warehouse_store'),
    path('feedback/', FeedbackView.as_view(), name='feedback'),
    path('client/', ClientView.as_view(), name='client_view'),
]
