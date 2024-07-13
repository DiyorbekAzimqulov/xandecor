from django.urls import path
from salesdoctorbot import views

urlpatterns = [
    path('', views.sales_doctor, name='sales_doctor'),
    path('fetch_warehouse_data/', views.fetch_warehouse_data, name='fetch_warehouse_data'),
]