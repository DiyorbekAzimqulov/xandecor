from typing import List
import requests
from environs import Env
from datetime import datetime, timedelta
from salesdoctorbot.models import Category, StockProduct, WareHouse, WareHouseProduct
from django.db.models import Sum, Q, F

# Load environment variables
env = Env()
env.read_env()

LOGIN_URL = env.str("SD_LOGIN_URL")
headers = {"Content-Type": "application/json"}
NAME_CATEGORY = "Xan Decor Naxt"


def get_warehouses(token: str, user_id: str) -> list:

    data = {
        "auth": {"userId": user_id, "token": token},
        "method": "getWarehouse",
        "params": {"page": 0, "limit": 10, "filter": {}},
    }

    # Send POST request to the API
    response = requests.post(LOGIN_URL, headers=headers, json=data)
    response_data = response.json()

    # Handle API response
    if response.status_code == 200 and response_data.get("status"):
        warehouses = response_data["result"]["warehouse"]
        extracted_data = [
            {"SD_id": wh["SD_id"], "name": wh["name"]} for wh in warehouses
        ]

        return {
            "status": True,
            "result": extracted_data,
            "pagination": response_data.get("pagination", {}),
        }
    else:
        return {
            "status": False,
            "error": response_data.get("error", "Failed to fetch warehouses"),
        }


def get_sales_categories(token: str, user_id: str) -> dict:

    data = {
        "auth": {
            "userId": user_id,
            "token": token,
        },
        "filial": {},
        "method": "getProductCategory",
        "params": {"page": 1, "limit": 100},
    }
    response = requests.post(LOGIN_URL, headers=headers, json=data)
    response_data = response.json()

    if response.status_code == 200 and response_data.get("status"):
        categories = response_data["result"]["productCategory"]
        extracted_data = [
            {
                "SD_id": cat["SD_id"],
                "name": cat["name"],
            }
            for cat in categories
        ]

        return {
            "status": True,
            "result": extracted_data,
            "pagination": response_data.get("pagination", {}),
        }

    else:
        return {
            "status": False,
            "error": response_data.get("error", "Failed to fetch sales categories"),
        }

def update_sold_ostatok_stock(token: str, user_id: str, warehouse_id: str, order_ids: List[str]) -> dict:
    if not order_ids:
        return {"error": "No product IDs provided to update Sold and Ostatok"}
    
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    data = {
        "auth": {
            "userId": user_id,
            "token": token
        },
        "filial": {
            "filial_id": "0"
        },
        "method": "getOrder",
        "params": {
            "page": 1,
            "limit": 100,
            "filter": {
                "status": [2, 3],
                "period": {
                    "dateLoad": {
                        "from": yesterday,
                        "to": today
                    }
                },
                "store": {
                    "SD_id": warehouse_id
                },
                "order": {
                    "SD_id": order_ids
                }
            }
        }
    }
    
    response = requests.post(LOGIN_URL, headers=headers, json=data)
    response_data = response.json()
    
    if response.status_code != 200:
        return {"error": "Failed to retrieve Sold and Ostatok"}
    
    if response_data.get("status"):
        orders = response_data["result"].get("order", [])
        if not orders:
            return {"error": "No orders found"}
        
        warehouse = WareHouse.objects.get(sd_id=warehouse_id)
        for order in orders:
            SD_id = order.get("SD_id")
            if SD_id is not None:
                order_products = order.get("orderProducts", [])
                for order_product in order_products:
                    quantity = order_product.get("quantity")
                    
                    try:
                        stock_product = StockProduct.objects.get(sd_id=SD_id)
                        warehouse_product = WareHouseProduct.objects.get(warehouse=warehouse, product=stock_product)
                        
                        if quantity is None:
                            warehouse_product.prixod = warehouse_product.ostatok  # Set prixod to ostatok if quantity is None
                        else:
                            warehouse_product.sold = quantity
                            warehouse_product.prixod = warehouse_product.ostatok + int(quantity)  # Calculate prixod based on ostatok + quantity
                        
                        warehouse_product.save()  # Save the warehouse_product instance after updating
                        
                    except StockProduct.DoesNotExist:
                        return {"error": f"Product with SD_id {SD_id} not found"}
                    except WareHouseProduct.DoesNotExist:
                        return {"error": f"Product with SD_id {SD_id} not found in warehouse {warehouse_id}"}
                    except Exception as e:
                        return {"error": f"Failed to update Sold and Ostatok: {e}"}
    else:
        return {"error": "Failed to retrieve Sold and Ostatok"}

    return {"success": "Sold and Ostatok updated successfully"}


def getProducts_by_WH_Ca(token: str, user_id: str, category_id: str) -> dict:
    data = {
        "auth": {"userId": user_id, "token": token},
        "method": "getStock",
        "params": {
            "category": {
                "SD_id": category_id,
            }
        }
    }

    response = requests.post(LOGIN_URL, headers=headers, json=data)
    response_data = response.json()

    if response.status_code != 200:
        return {"error": "Failed to retrieve products by warehouse and category"}

    if response_data.get("status"):
        warehouses = response_data["result"].get("warehouse", [])
        for warehouse in warehouses:
            warehouse_name = warehouse.get("name")
            warehouse_id = warehouse.get("SD_id")
            products = warehouse.get("products", [])
            warehouse_obj, _ = WareHouse.objects.update_or_create(sd_id=warehouse_id, defaults={'name': warehouse_name})
            category_obj, _ = Category.objects.update_or_create(sd_id=category_id, defaults={'name': NAME_CATEGORY})
            for product in products:
                product_name = product.get("name")
                product_id = product.get("SD_id")
                quantity = product.get("quantity") or 0
                if quantity > 0:
                    product_obj, _ = StockProduct.objects.update_or_create(sd_id=product_id, defaults={'name': product_name})
                    WareHouseProduct.objects.update_or_create(
                        warehouse=warehouse_obj,
                        product=product_obj,
                        category=category_obj,
                        defaults={'ostatok': quantity}
                    )
    else:
        return {"error": response_data.get("error", "Failed to retrieve data")}

    return {"success": "Products updated successfully"}

# def getStoreLogs(token: str, user_id: str, warehouse_id: str, category_id: str) -> dict:
#     data = {
#         "auth": {"userId": user_id, "token": token},
#         "method": "getStoreLogs",
#         "params": {
#             "storeId": warehouse_id,
#         }
#     }
    
#     response = requests.post(LOGIN_URL, headers=headers, json=data)
#     response_data = response.json()
    
#     if response.status_code != 200:
        