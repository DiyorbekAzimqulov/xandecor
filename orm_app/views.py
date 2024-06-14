from django.contrib.auth.mixins import AccessMixin
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic import DetailView, ListView

from .models import Container, User, AskUser, Organization, Sale
from .services import (
    get_review_statistics_by_container,
    get_reviewers_statistics_by_user,
)
from .services import (
    get_review_statistics_by_container,
    get_reviewers_statistics_by_user,
    get_products_statistics_by_date,
)
from django.contrib.auth.mixins import AccessMixin
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import requests
from salebot.data.config import BOT_TOKEN
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt


class SuperuserRequiredMixin(AccessMixin):
    """Ensure that the current user is authenticated and is a superuser."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class IndexView(SuperuserRequiredMixin, ListView):
    model = Container
    template_name = "containers.html"
    context_object_name = "containers"
    paginate_by = 10

    def get_queryset(self):
        return Container.objects.all().order_by("id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.all()
        context["active_page"] = "containers_list"
        return context


class ContainerDetailView(SuperuserRequiredMixin, DetailView):
    model = Container
    template_name = "container_detail.html"
    context_object_name = "container"

    def get_queryset(self):
        return Container.objects.filter(id=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["review_statistics"] = get_review_statistics_by_container(
            self.kwargs["pk"]
        )
        context["active_page"] = "containers_list"
        return context


class ReviewersView(SuperuserRequiredMixin, ListView):
    model = User
    template_name = "reviewers.html"
    context_object_name = "reviewers"
    paginate_by = 10

    def get_queryset(self):
        return User.objects.filter().order_by("id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reviewers"] = User.objects.all()
        context["active_page"] = "reviewers"
        return context


class ReviewerDetailView(SuperuserRequiredMixin, DetailView):
    model = User
    template_name = "reviewer_detail.html"
    context_object_name = "reviewer"

    def get_queryset(self):
        return User.objects.filter(id=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reviewer_statistics"] = get_reviewers_statistics_by_user(
            self.kwargs["pk"]
        )
        context["active_page"] = "reviewers"
        return context
    
        
class ProductsStatisticsView(SuperuserRequiredMixin, ListView):
    model = User
    template_name = "products_statistics.html"
    context_object_name = "products"

    def get_queryset(self):
        return User.objects.filter().order_by("id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from_date = self.kwargs["from_date"]
        to_date = self.kwargs["to_date"]
        context["statistics"] = get_products_statistics_by_date(from_date, to_date)
        context["active_page"] = "products_statistics"
        return context


class AskedUsersView(SuperuserRequiredMixin, ListView):
    model = AskUser
    template_name = 'asked_users.html'
    context_object_name = 'asked_users'
    paginate_by = 10

    def get_queryset(self):
        return AskUser.objects.all().order_by('id')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asked_users'] = AskUser.objects.all()
        context['organizations'] = Organization.objects.all()
        context['active_page'] = 'asked_users'
        return context


def accept_user(request, pk):
    user = get_object_or_404(AskUser, pk=pk)
    organizations = Organization.objects.all()
    response = {
        'status': 'show_organizations',
        'user_id': user.id,
        'organizations': list(organizations.values())
    }
    return JsonResponse(response)

def reject_user(request, pk):
    user = get_object_or_404(AskUser, pk=pk)
    # Format the data into a readable string
    
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {'chat_id': user.telegram_id, 'text': "Sizning arizangiz rad etildi!"}
    response = requests.post(url, data=payload)

    response = {
        'status': 'rejected',
        'user_id': user.id
    }
    return JsonResponse(response)

def save_user_with_organizations(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        organization_ids = request.POST.getlist('organization_ids[]')
        user = get_object_or_404(AskUser, pk=user_id)
        new_user = User.objects.create(
            name=user.first_name + " " + user.last_name,
            telegram_id=user.telegram_id,
            phone_number=user.phone_number
        )
        organizations = Organization.objects.filter(id__in=organization_ids)
        new_user.organizations.set(organizations)
        user.delete()
        response = {'status': 'success'}
        url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
        payload = {'chat_id': user.telegram_id, 'text': "Sizning arizangiz qabul qilindi! Botimizdan foydalanishga ruxsat berildi! /start buyrug'ini bosing!"}
        requests.post(url, data=payload)
        return JsonResponse(response)
    return JsonResponse({'status': 'error'}, status=400)


class ContainerOrdersDetailView(SuperuserRequiredMixin, ListView):
    template_name = 'container_orders.html'

    def get(self, request, container_id):
        container = get_object_or_404(Container, id=container_id)
        users = User.objects.filter(sale__container=container).distinct()

        def user_has_missing_purchase_date(user):
            return Sale.objects.filter(user=user, container=container, purchase_date__isnull=True).exists()

        users_with_indicators = [(user, user_has_missing_purchase_date(user)) for user in users]
        

        context = {
            'container': container,
            'users_with_indicators': users_with_indicators,
        }
        return render(request, self.template_name, context)
    

class UserOrdersView(SuperuserRequiredMixin, ListView):
    template_name = 'user_orders.html'

    def get(self, request, user_id, container_id):
        user = get_object_or_404(User, id=user_id)
        sales = Sale.objects.filter(user=user, container_id=container_id)

        def has_missing_purchase_date(sale):
            return sale.purchase_date is None

        sales_with_indicators = [(sale, has_missing_purchase_date(sale)) for sale in sales]

        total_price = sum(sale.price for sale in sales)
        
        context = {
            'user': user,
            'sales_with_indicators': sales_with_indicators,
            'total_price': total_price,
            
        }
        return render(request, self.template_name, context)


class RequestedOrdersView(SuperuserRequiredMixin, ListView):
    template_name = 'requested_orders.html'
    model = Sale

    def get_queryset(self):
        # if the container is null with the purchase date, it means the order is requested
        return Sale.objects.filter(Q(container__isnull=True))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'requested_orders'
        return context


@csrf_exempt
def report_location(request):
    if request.method == 'POST':
        location_name = request.POST.get('location_name')
        containers = request.POST.get('containers').split(',')
        for container_id in containers:
            user, container, product = Sale.objects.filter(container_id=container_id).select_related('user', 'container', 'product').first()
            context = {
                    f"📌 Location: {location_name}\n"
                    f"# Container Number: {container.number}\n"
                    f"📦 Product: {product.name}\n"
                    f"📅 Arrival Date: {container.arrival_date}\n"
                    f"🧑‍💼 User: {user.username}\n"
            }
            
            url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
            payload = {'chat_id': user.telegram_id, 'text': context}
            response = requests.post(url, data=payload)
            
        return JsonResponse(response)
    return JsonResponse({'status': 'failed'}, status=400)