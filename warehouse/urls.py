from django.urls import path
from warehouse.views import WarehouseView, WareHouseStoreView, StoreDetailView, edit_shelf

urlpatterns = [
    path("", WarehouseView.as_view(), name="warehouse_list"),
    path('<int:id>', WareHouseStoreView.as_view(), name="wareHouse"),
    path('store/<int:id>/', StoreDetailView.as_view(), name='store_detail'),
    path('warehouse-product-detail/<int:id>/', WareHouseStoreView.as_view(), name='warehouse_product_detail'),
    path('edit_shelf/', edit_shelf, name='edit_shelf'),  # Add this line
]
