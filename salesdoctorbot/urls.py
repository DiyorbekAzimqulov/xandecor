from django.urls import path
from .views import (
    SalesDoctorView, 
    ShipProductView, 
    RedistributeProductView,
    ForgottenShipment,
    DiscountProductView,
    RemoveDiscountEventView
    )

urlpatterns = [
    path('', SalesDoctorView.as_view(), name='sales_doctor'),
    path('ship/', ShipProductView.as_view(), name='ship_product'),
    path('redistribute/', RedistributeProductView.as_view(), name='redistribute_product'),
    path('forgotten/', ForgottenShipment.as_view(), name='forgotten_product'),
    path('discount/', DiscountProductView.as_view(), name='discount_product'),
    path('discount/remove/<int:event_id>/', RemoveDiscountEventView.as_view(), name='remove_discount_event'),
    ]