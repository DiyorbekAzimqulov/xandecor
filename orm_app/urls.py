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
    ContainerOrdersDetailView,
    UserOrdersView,
    RequestedOrdersView,
    report_location,
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
    path('<int:container_id>/users/', ContainerOrdersDetailView.as_view(), name='container_orders'),
    path('u<int:user_id>/c<int:container_id>/orders/', UserOrdersView.as_view(), name='user_orders'),
    path('requested-orders/', RequestedOrdersView.as_view(), name='requested_order'),
    path('report-location/', report_location, name='report-location'),
]
