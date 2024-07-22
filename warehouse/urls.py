from django.urls import path
from warehouse.views import WarehouseView, WareHouseStoreView, StoreDetailView

urlpatterns = [
    path("", WarehouseView.as_view(), name="warehouse_list"),
    path('<int:id>', WareHouseStoreView.as_view(), name="wareHouse"),
    path('store/<int:id>/', StoreDetailView.as_view(), name='store_detail'),  # Assuming you have a StoreDetailView
    path('warehouse-product-detail/<int:id>/', WareHouseStoreView.as_view(), name='warehouse_product_detail'),
    ]

