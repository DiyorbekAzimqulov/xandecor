from django.urls import path
from .views import (
    IndexView,
    ContainerDetailView,
    ReviewersView,
    ReviewerDetailView,
    ProductsStatisticsView,
    AskedUsersView,
    accept_user,
    save_user_with_organizations,
    reject_user,
    container_orders,
    user_orders,
)

urlpatterns = [
    path("", IndexView.as_view(), name="containers_list"),
    path("c-detail/<int:pk>/", ContainerDetailView.as_view(), name="container-detail"),
    path("reviewers/", ReviewersView.as_view(), name="reviewers"),
    path("r-detail/<int:pk>/", ReviewerDetailView.as_view(), name="reviewer-detail"),
    path(
        "pdts-st/<str:from_date>_<str:to_date>/",
        ProductsStatisticsView.as_view(),
        name="products-statistics",
    ),
    path('asked-users/', AskedUsersView.as_view(), name='asked_users'),
    path('accept-user/<int:pk>/', accept_user, name='accept_user'),
    path('save-user-with-organizations/', save_user_with_organizations, name='save_user_with_organizations'),
    path('reject-user/<int:pk>/', reject_user, name='reject_user'),
    path('<int:container_id>/orders/', container_orders, name='container_orders'),
    path('user/<int:user_id>/orders/', user_orders, name='user_orders'),

]
