from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import views as auth_views

from django.urls import include


class MyLoginView(auth_views.LoginView):

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

class MyLogoutView(auth_views.LogoutView):

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    

urlpatterns = [
    path("admin/", admin.site.urls),
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', MyLogoutView.as_view(next_page='/login/'), name='logout'),
    path("containers/", include("orm_app.urls")),
    path("sales-doctor/", include("salesdoctorbot.urls")),
    path("warehouse/", include("warehouse.urls")),
    path("", include("website.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

