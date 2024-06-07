from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.base, name='home'),
    path('category/', views.category, name='category'),
    path('contact/', views.contact, name='contact'),
    path('investor/', views.team, name='team'),
    path('service/', views.service, name='service'),
    path('led/<int:category_id>/', views.select_category_led, name='select_category_led'),
    path('wallpaper/<int:category_id>/', views.select_category_wallpaper, name='select_category_wallpaper'),
    path('wallpapers/', views.wallpapers, name='wallpapers'),
    path('leds/', views.leds, name='leds'),
    path('submit-service/', views.submit_service, name='submit_service'),
    path('submit-contact/', views.submit_contact, name='submit_contact'),
    path('submit-base/', views.submit_base, name='submit_base'),
    path('news-detail/<int:news_id>/', views.news_detail, name='news_detail'),
    path('news/', views.news_list, name='news'),
    path('set-language/<str:language>/', views.set_language, name='set_language'),
    ]