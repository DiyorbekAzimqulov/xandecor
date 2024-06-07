from aiogram import Bot, Dispatcher, executor, types
import requests

from .models import AboutUs, CarouselMainPhoto

def get_about_us(request):
    abo = AboutUs.objects.first()
    return  {'about_social': abo}

def get_carousel_main_photo(request):
    carousels = CarouselMainPhoto.objects.all()
    return {'carousels': carousels}




TOKEN = '6758620513:AAHncQliZ2W2nGlPrPHJQHQwGhXNXSKaIek'
CHAT_ID = '1240798052'

def send_message_notify_quote(data: dict) -> None:
    # Format the data into a readable string
    message = (
        "✨ New Submission on Quote of WebSite ✨\n\n"
        f"👤 Name: {data.get('name', 'N/A')}\n"
        f"✉️ Email: {data.get('email', 'N/A')}\n"
        f"📱 Mobile: {data.get('mobile', 'N/A')}\n"
        f"🛠 Service: {data.get('service', 'N/A')}\n"
        f"📝 Note: {data.get('note', 'N/A')}"
    )

    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': message}

    response = requests.post(url, data=payload)

    # Check the response status
    if response.status_code != 200:
        print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
