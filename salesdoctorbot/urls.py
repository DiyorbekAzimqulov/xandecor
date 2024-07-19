from django.urls import path
from .views import SalesDoctorView, ShipProductView, RedistributeProductView

urlpatterns = [
    path('', SalesDoctorView.as_view(), name='sales_doctor'),
    path('ship/', ShipProductView.as_view(), name='ship_product'),
    path('redistribute/', RedistributeProductView.as_view(), name='redistribute_product')
    
]