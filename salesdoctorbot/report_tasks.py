import requests
from salesdoctorbot.models import WareHouse, WareHouseProduct
from salesdoctorbot.salesDoctorAuth import auth_sales_doctor
from salesdoctorbot.services import getProducts_by_WH_Ca, update_sold_ostatok_stock
from salesdoctorbot.data.config import CATEGORY_ID, GROUP_ID, BOT_TOKEN
from salesdoctorbot.report_functions import (
    ship_db_data, ship_products, 
    redistribute_products, 
    redistribute_data, 
    find_forgotten_shipments, 
    generate_forgotten_shipment_report
)
from orm_app.models import Product, DiscountEvent, TelegramGroup

TELEGRAM_MESSAGE_LIMIT = 4096  # Telegram message character limit

def split_message(message, max_length=TELEGRAM_MESSAGE_LIMIT):
    """Splits a long message into chunks of max_length characters."""
    return [message[i:i+max_length] for i in range(0, len(message), max_length)]

def send_telegram_message(chat_id, text):
    """Sends a message to the specified Telegram chat."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # Split the message if it's too long
    messages = split_message(text)
    
    for msg in messages:
        params = {
            'chat_id': chat_id,
            'text': msg,
        }
        response = requests.post(url, data=params)
        if response.status_code != 200:
            return f"Error sending message: {response.status_code} - {response.text}"
    
    return "Message sent successfully"

def send_telegram_photo(chat_id, photo_url, caption):
    """Sends a photo to the specified Telegram chat."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    params = {
        'chat_id': chat_id,
        'photo': photo_url,
        'caption': caption,
    }
    response = requests.post(url, data=params)
    return response.status_code

def daily_shipping_report() -> str:
    token, user_id = auth_sales_doctor()
    if token and user_id:
        getProducts_by_WH_Ca(token, user_id, CATEGORY_ID)
        
        # All other warehouses
        warehouses = list(WareHouse.objects.all())
        for warehouse in warehouses:
            order_ids = list(WareHouseProduct.objects.filter(warehouse=warehouse).values_list('product__sd_id', flat=True))
            print("Updating Products ...")
            update_sold_ostatok_stock(token, user_id, warehouse.sd_id, order_ids)
            print("Products Updated")
        
        shipping_db = ship_db_data()
        _, report = ship_products(shipping_db)

        return send_telegram_message(GROUP_ID, report)

def daily_redistribute_report() -> str:            
    redistribute_db = redistribute_data()
    _, redistribute_report = redistribute_products(redistribute_db)
    
    return send_telegram_message(GROUP_ID, redistribute_report)

def daily_forgotten_shipments() -> str:
    forgotten_shipments = find_forgotten_shipments()
    report = generate_forgotten_shipment_report(forgotten_shipments)
    
    return send_telegram_message(GROUP_ID, report)

def daily_discount_event() -> str:
    discount_events = DiscountEvent.objects.all()
    for event in discount_events:
        products = list(event.products.all())
        groups = list(event.group.all().select_related('group_id'))
        discount = event.discount
        
        for product in products:
            message = f"Product: {product.name}\nDiscount: {discount}%"
            photo1_url = product.image1.url
            photo2_url = product.image2.url

            for group in groups:
                group_id = group.group_id
                
                # Send first image
                status_code1 = send_telegram_photo(group_id, photo1_url, "")
                if status_code1 != 200:
                    return f"Error sending first photo to group {group.name}"
                
                # Send second image
                status_code2 = send_telegram_photo(group_id, photo2_url, message)
                if status_code2 != 200:
                    return f"Error sending second photo to group {group.name}"
        
        # Subtract 1 from report_count and save the event
        event.report_count -= 1
        if event.report_count <= 2:
            event.delete()
        else:
            event.save()
    
    return "Discount event reports sent successfully"
