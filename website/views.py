from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from . import models
from website.service import send_message_notify_quote
from django.utils.translation import gettext as _
from django.http import HttpResponseRedirect
from django.utils import translation
from django.urls import reverse
from orm_app.models import Product, Category
from django.views.decorators.csrf import csrf_exempt

def base(request):
    """Base view for the wallpaper app."""
    categorywallpapers = Category.objects.all()
    categoryleds = models.CategoryLed.objects.all()
    wallpapers = Product.objects.all()[:6]
    last_news = models.News.objects.last()
    services = models.Service.objects.all()[:3]
    partners = models.Brands.objects.all()
    diogram_analysis = models.DiagramAnalysis.objects.last()
    teams = models.Teams.objects.all()[:4]
    leds = models.Leds.objects.all()[:6]
    context = {
        'categorywallpapers': categorywallpapers,
        'categoryleds': categoryleds,
        'wallpapers': wallpapers,
        'services': services,
        'partners': partners,
        'diogram_analysis': diogram_analysis,
        'teams': teams,
        'last_news': last_news,
        'leds': leds,
        'base': 'active'
    }
    return render(request=request, template_name='layout/base.html', context=context)




def category(request):
    all_leds = models.Leds.objects.all()
    all_wallcovers = Category.objects.all()

    # Combine wallpaper and LED categories into a single list
    context = {
        'all_leds': all_leds,
        'all_wallcovers': all_wallcovers,
        'category': 'active'  # Set 'category' to 'active'
    }
    return render(request=request, template_name='category.html', context=context)



def wallpapers(request):
    wallcovers = Product.objects.all()
    categories_wallpaper = Category.objects.all()
    context = {'wallcovers': wallcovers, 'categories_wallpaper': categories_wallpaper}
    return render(request, 'wallpapers.html', context)

def select_category_wallpaper(request, category_id):
    category = Category.objects.get(id=category_id)
    wallcovers = Product.objects.filter(category=category)
    categories_wallpaper = Category.objects.all()
    context = {'category': category, 'wallcovers': wallcovers, 'categories_wallpaper': categories_wallpaper}
    return render(request, 'wallpapers.html', context)

def leds(request):
    leds = models.Leds.objects.all()
    categories_led = models.CategoryLed.objects.all()
    context = {'leds': leds, 'categories_led': categories_led}
    return render(request, 'leds.html', context)

def select_category_led(request, category_id):
    category = models.CategoryLed.objects.get(id=category_id)
    leds = models.Leds.objects.filter(category=category)
    categories_led = models.CategoryLed.objects.all()
    context = {'category': category, 'leds': leds, 'categories_led': categories_led}
    return render(request, 'leds.html', context)



def news(request):
    news_data = models.About.objects.all()
    context = {'news_data': news_data, 'news': 'active'}
    return render(request=request, template_name='about.html', context=context)

def contact(request):
    """Contact view for the wallpaper app."""
    return render(request=request, template_name='contact.html', context={'contact': 'active'})


def team(request):
    """Investor view for the wallpaper app."""
    teams = models.Teams.objects.all()
    context = {'teams': teams, 'team': 'active'}
    return render(request=request, template_name='team.html', context=context)


def service(request):
    """Service view for the wallpaper app."""
    services = models.Service.objects.all()
    context = {'services': services, 'service': 'active'}
    return render(request=request, template_name='service.html', context=context)


@csrf_exempt
def submit_service(request):
    if request.method == 'POST':
        # Extract data from the form
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        service_id = request.POST.get('service')
        note = request.POST.get('note')

        # Check if service_id is a valid integer
        try:
            service_id = int(service_id)
        except ValueError:
            return HttpResponse("Invalid service ID")

        # Fetch the service object from the database
        try:
            service = models.Service.objects.get(id=service_id)
        except models.Service.DoesNotExist:
            return HttpResponse("Service not found")

        # Create a new Quote object and save it to the database
        quote = models.Quote(name=name, email=email, mobile=mobile, service=service, note=note)
        quote.save()

        # Prepare data to send to the bot
        data = {
            'name': name,
            'email': email,
            'mobile': mobile,
            'service': service,
            'note': note
        }
        send_message_notify_quote(data=data)


        # Redirect or return a success response
        return render(request, 'success.html')  # Replace with your actual success page template name

    # Handle GET request if needed
    else:
        # Render the form page
        return render(request, 'service.html', {'services': models.Service.objects.all()})

@csrf_exempt
def submit_base(request):
    if request.method == 'POST':
        # Extract data from the form
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        note = request.POST.get('note')

        # Create a new Quote object and save it to the database
        quote = models.Quote(name=name, email=email, mobile=mobile, note=note)
        quote.save()

        # Prepare data to send to the bot
        data = {
            'name': name,
            'email': email,
            'mobile': mobile,
            'note': note
        }
        send_message_notify_quote(data=data)

        # Redirect or return a success response
        return render(request, 'success.html')  # Replace 'success.html' with your actual success page template name

    # Handle GET request if needed
    else:
        # Render the form page
        return render(request, 'layout/base.html')
    
@csrf_exempt
def submit_contact(request):
    if request.method == 'POST':
        # Extract data from the form
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Create a new Contact object and save it to the database
        contact = models.Contact(name=name, email=email, subject=subject, message=message)
        contact.save()

        # Prepare data to send to the bot
        data = {
            'name': name,
            'email': email,
            'subject': subject,
            'message': message
        }
        send_message_notify_quote(data=data)

        # Redirect or return a success response
        return render(request, 'success.html')

    # Handle GET request if needed
    else:
        # Render the form page
        return render(request, 'contact.html')


def news_list(request):
    news_list = models.News.objects.all()
    return render(request, 'about.html', {'news_list': news_list, 'news': 'active'})

def news_detail(request, news_id):
    news_item = get_object_or_404(models.News, id=news_id)
    return render(request, 'detail.html', {'news_item': news_item})


def set_language(request, language):
    next_page = request.POST.get('next', request.GET.get('next', '/'))
    if language:
        translation.activate(language)
        request.session['django_language'] = language
    return HttpResponseRedirect(next_page)
