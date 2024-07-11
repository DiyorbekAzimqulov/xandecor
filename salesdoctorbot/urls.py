from django.urls import path
from salesdoctorbot import views

urlpatterns = [
    path('', views.sales_doctor, name='sales_doctor'),
]