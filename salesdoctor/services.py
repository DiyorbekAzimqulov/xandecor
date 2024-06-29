import requests
from environs import Env
from datetime import datetime, timedelta
# Load environment variables
env = Env()
env.read_env()

LOGIN_URL = env.str("SD_LOGIN_URL")
headers = {"Content-Type": "application/json"}


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
        

def get_sold_ostatok_stock(token: str, user_id: str, warehouse_id: str, order_id: str) -> dict:    
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
                    "SD_id": order_id
                }
            }
        }
    } 
    response = requests.post(LOGIN_URL, headers=headers, json=data)
    response_data = response.json()
    
    if response.status_code == 200 and response_data.get("status"):
        order = response_data["result"].get("order")
        if order:
            orderProducts = order[0].get("orderProducts", [])
            product_name = orderProducts[0].get("product", {}).get("name", "Unknown Product")
            quantity = orderProducts[0].get("quantity", 0)
            return {
                "status": True,
                "product_name": product_name,
                "quantity": quantity,
            }
        else:
            return {
                "status": False,
                "error": "No orders found",
            }
        
    else:
        return {
            "status": False,
            "error": response_data.get("error", "Failed to fetch sold stock"),
        }

    
    
def get_sales_stock(token: str, user_id: str, warehouse_id: str, category_id: str) -> dict:
    data = {
        "auth": {"userId": user_id, "token": token},
        "method": "getStock",
        "params": {
            "store": {
                "SD_id": warehouse_id,
            },
            "category": {
                "SD_id": category_id,
            }
        }
    }
    
    response = requests.post(LOGIN_URL, headers=headers, json=data)
    response_data = response.json()
    
    if response.status_code == 200 and response_data.get("status"):
        warehouse = response_data["result"]["warehouse"]
        products = warehouse[0].get("products", [])
        extracted_data = []
        for product in products:
            solds_ostatok = get_sold_ostatok_stock(token, user_id, warehouse_id, product["SD_id"])
            if solds_ostatok["status"]:
                prixod = product["quantity"] if product["quantity"] is not None else 0
                sold = solds_ostatok["quantity"] if solds_ostatok["quantity"] is not None else 0
                ostatok = prixod - sold
                
                extracted_data.append({
                    "prixod": prixod,
                    "product_name": solds_ostatok["product_name"],
                    "sold": sold,
                    "ostatok": ostatok
                })
            else:
                return {
                    "status": False,
                    "error": solds_ostatok["error"],
                }
        return {
            "status": True,
            "result": extracted_data,
        }
    else:
        return {
            "status": False,
            "error": response_data.get("error", "Failed to fetch sales stock"),
        }
