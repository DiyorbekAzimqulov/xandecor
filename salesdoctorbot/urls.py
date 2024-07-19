from django.urls import path
from .views import SalesDoctorView, ShipProductView

urlpatterns = [
    path('', SalesDoctorView.as_view(), name='sales_doctor'),
    path('ship/', ShipProductView.as_view(), name='ship_product'),
]