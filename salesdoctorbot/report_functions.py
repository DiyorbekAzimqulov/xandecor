from salesdoctorbot.models import WareHouse, StockProduct, WareHouseProduct
from django.db.models import Prefetch
import html
import asyncio

MIN_PRODUCT_UNIT = 26
MAX_PRODUCT_UNIT = 32
BATCH_SIZE = 6
LESS_PRODUCT = 15
TELEGRAM_MESSAGE_LIMIT = 4096
SALE_PERCENTAGE_THRESHOLD = 10


def ship_db_data() -> dict:
    # Filter only the required warehouses
    warehouses = WareHouse.objects.all()
    products = StockProduct.objects.all()
    warehouse_products = WareHouseProduct.objects.select_related('warehouse', 'product').all()
    
    # Prefetch the related objects
    warehouse_products_prefetch = Prefetch(
        'warehouseproduct_set',
        queryset=warehouse_products,
        to_attr='warehouse_products'
    )
    
    # Use prefetch_related to reduce the number of queries
    warehouses = warehouses.prefetch_related(warehouse_products_prefetch)
    
    shipping_db = {}
    for product in products:
        units = []
        for warehouse in warehouses:
            # Find the related warehouse product from the prefetched data
            warehouse_product = next(
                (wp for wp in warehouse.warehouse_products if wp.product_id == product.id), 
                None
            )
            if warehouse_product:
                units.append(
                    {
                        "name": warehouse.name,
                        "units": warehouse_product.ostatok,
                        "sold_units": warehouse_product.sold,
                        "is_main": warehouse.name == "Основной склад"
                    }
                )
        shipping_db[product.name] = units
    return shipping_db


def ship_products(shipping_db):
    report_data = {}
    for product, warehouses in shipping_db.items():
        main_warehouse = None
        for wh in warehouses:
            if wh["is_main"]:
                main_warehouse = wh
                break

        if not main_warehouse:
            continue  # If no main warehouse is found, skip to the next product

        # Sort sub-warehouses by sold_units in descending order
        sub_warehouses = sorted(
            [wh for wh in warehouses if not wh["is_main"]],
            key=lambda x: x["sold_units"],
            reverse=True,
        )

        for sub_warehouse in sub_warehouses:
            current_units = sub_warehouse["units"]
            total_units_to_ship = 0
            while current_units < MIN_PRODUCT_UNIT and main_warehouse["units"] > 0:
                if main_warehouse["units"] >= BATCH_SIZE:
                    units_to_ship = BATCH_SIZE
                else:
                    units_to_ship = main_warehouse["units"]

                current_units += units_to_ship
                main_warehouse["units"] -= units_to_ship
                sub_warehouse["units"] = current_units
                total_units_to_ship += units_to_ship
            if total_units_to_ship > 0:
                if sub_warehouse["name"] not in report_data:
                    report_data[sub_warehouse["name"]] = []
                report_data[sub_warehouse["name"]].append(
                    {
                        "product_name": product,
                        "total_units_to_ship": total_units_to_ship
                    }
                )

    # Generate the report text
    report = ""
    for sub_warehouse_name, entries in report_data.items():
        report += f"📦 {html.escape(sub_warehouse_name)}:\n"
        for entry in entries:
            report += f"⬇️ {html.escape(entry['product_name'])} → {entry['total_units_to_ship']} Aboi\n"
        report += "\n"

    return report_data, report.strip()



def redistribute_data() -> dict:
    try:
        main_warehouse = WareHouse.objects.get(name="Основной склад")
    except WareHouse.DoesNotExist:
        return {"error": "Main warehouse 'Основной склад' not found."}

    # Get products from the main warehouse with zero ostatok
    main_warehouse_products = WareHouseProduct.objects.filter(warehouse=main_warehouse, ostatok__gt=0).select_related('product')
    distribute_db = {}
    for main_product in main_warehouse_products:
        product_name = main_product.product.name
        distribute_db[product_name] = []

        # Add subwarehouse data
        subwarehouse_products = WareHouseProduct.objects.filter(
            product=main_product.product, ostatok__gt=0
        ).exclude(warehouse=main_warehouse)

        # Filter only the required subwarehouses
        valid_subwarehouses = ["Склад-VS (O'RIKZOR)", "Склад-VS (Jomiy)", "Склад-VS (QO'YLIQ)", "Склад-VS (BEKTOP)"]
        for sub_product in subwarehouse_products:
            if sub_product.warehouse.name in valid_subwarehouses:
                subwarehouse_data = {
                    "name": sub_product.warehouse.name,
                    "is_main": False,
                    "remained_units": sub_product.ostatok,
                    "sold_units": sub_product.sold,
                    "initial_units": sub_product.prixod,
                    "sale_percentage": (sub_product.sold / sub_product.prixod) * 100 if sub_product.prixod > 0 else 0
                }
                distribute_db[product_name].append(subwarehouse_data)

    return distribute_db



def update_sale_percentage(warehouse):
    total_units = warehouse["remained_units"] + warehouse["sold_units"]
    if total_units > 0:
        warehouse["sale_percentage"] = round(
            (warehouse["sold_units"] / total_units) * 100
        )
    else:
        warehouse["sale_percentage"] = 0


def redistribute_products(db):
    report = ""
    helper = {}

    for product, warehouses in db.items():
        low_sales_warehouses = sorted(
            [
                wh
                for wh in warehouses
                if wh["sale_percentage"] < SALE_PERCENTAGE_THRESHOLD
            ],
            key=lambda x: x["sale_percentage"],
        )
        high_sales_warehouses = sorted(
            [
                wh
                for wh in warehouses
                if wh["sale_percentage"] >= SALE_PERCENTAGE_THRESHOLD
            ],
            key=lambda x: x["sale_percentage"],
            reverse=True,
        )
        while low_sales_warehouses and high_sales_warehouses:
            no_transfer_made = True

            for high_sales_warehouse in high_sales_warehouses:
                for low_sales_warehouse in low_sales_warehouses:
                    if low_sales_warehouse["remained_units"] == 0:
                        continue

                    transfer_units = low_sales_warehouse["remained_units"]
                    if transfer_units > BATCH_SIZE:
                        transfer_units = BATCH_SIZE
                    low_sales_warehouse["remained_units"] -= transfer_units
                    high_sales_warehouse["remained_units"] += transfer_units
                    location_product = (
                        product,
                        low_sales_warehouse["name"],
                        high_sales_warehouse["name"],
                    )
                    if location_product in helper:
                        helper[location_product] += transfer_units
                    else:
                        helper[location_product] = transfer_units
                    # Update sale percentages
                    update_sale_percentage(low_sales_warehouse)
                    update_sale_percentage(high_sales_warehouse)

                    no_transfer_made = False

                    # If high sales warehouse sale percentage falls below threshold, stop distributing to it
                    if (
                        high_sales_warehouse["sale_percentage"]
                        < SALE_PERCENTAGE_THRESHOLD
                    ):
                        break
                # Remove high sales warehouses with 100% sales or above the threshold
                high_sales_warehouses = [
                    wh
                    for wh in high_sales_warehouses
                    if wh["sale_percentage"] >= SALE_PERCENTAGE_THRESHOLD
                ]
                # If no more low sales warehouses, break
                if not low_sales_warehouses:
                    break

            # Remove low sales warehouses with no remaining units
            low_sales_warehouses = [
                wh for wh in low_sales_warehouses if wh["remained_units"] > 0
            ]

            # Break if no transfer was made in this iteration to avoid infinite loop
            if no_transfer_made:
                break

    for location_product, units in helper.items():
        report += f"{location_product[1]} ↗️ {units} shit {location_product[0]} ➡️ {location_product[2]}\n"

    return helper, report.strip()

def find_forgotten_shipments():
    # Get the main warehouse
    
    main_warehouse = WareHouse.objects.get(name="Основной склад")

    # Get products in the main warehouse with non-zero ostatok
    main_warehouse_products = WareHouseProduct.objects.filter(
        warehouse=main_warehouse,
        ostatok__gt=0
    ).select_related('product')

    # Find products that have no stock, sold, or incoming in all other warehouses
    forget_products = []
    for warehouse_product in main_warehouse_products:
        # Check if the product exists in any other warehouse
        other_warehouses_products = WareHouseProduct.objects.filter(
            product=warehouse_product.product
        ).exclude(warehouse=main_warehouse)

        # Check if all other warehouses have ostatok, sold, and prixod equal to 0
        if all(other_warehouse_product.ostatok == 0 and 
               other_warehouse_product.sold == 0 and 
               other_warehouse_product.prixod == 0 
               for other_warehouse_product in other_warehouses_products):
            forget_products.append(warehouse_product)

    return forget_products
    

def generate_forgotten_shipment_report(forget_products):
    if not forget_products:
        return "Hech qanday unutilgan mahsulot topilmadi."

    report_lines = ["🔍 Unutilgan Mahsulotlar Hisoboti:"]
    
    for product in forget_products:
        report_lines.append(
            f"Mahsulot: {product.product.name}, "
            f"Ombor: {product.warehouse.name}, \n"
            f"📊 Ostatok: {product.ostatok}, "
            f"🔽 Sotilgan: {product.sold}, "
            f"🔼 Prixod: {product.prixod}"
        )

    return "\n".join(report_lines)



"""
def ship_db_data() -> dict:
    warehouses = WareHouse.objects.all()
    products = StockProduct.objects.all()
    warehouse_products = WareHouseProduct.objects.select_related('warehouse', 'product').all()
    
    # Prefetch the related objects
    warehouse_products_prefetch = Prefetch(
        'warehouseproduct_set',
        queryset=warehouse_products,
        to_attr='warehouse_products'
    )
    
    # Use prefetch_related to reduce the number of queries
    warehouses = warehouses.prefetch_related(warehouse_products_prefetch)
    
    shipping_db = {}
    for product in products:
        units = []
        for warehouse in warehouses:
            # Find the related warehouse product from the prefetched data
            warehouse_product = next(
                (wp for wp in warehouse.warehouse_products if wp.product_id == product.id), 
                None
            )
            if warehouse_product:
                units.append(
                    {
                        "name": warehouse.name,
                        "units": warehouse_product.ostatok,
                        "sold_units": warehouse_product.sold,
                        "is_main": warehouse.name == "Основной склад"
                    }
                )
        shipping_db[product.name] = units
    return shipping_db


def ship_products(shipping_db):
    report = ""
    for product, warehouses in shipping_db.items():
        main_warehouse = None
        for wh in warehouses:
            if wh["is_main"]:
                main_warehouse = wh
                break

        if not main_warehouse:
            continue  # If no main warehouse is found, skip to the next product

        # Sort sub-warehouses by sold_units in descending order
        sub_warehouses = sorted(
            [wh for wh in warehouses if not wh["is_main"]],
            key=lambda x: x["sold_units"],
            reverse=True,
        )

        for sub_warehouse in sub_warehouses:
            current_units = sub_warehouse["units"]
            total_units_to_ship = 0
            while current_units < MIN_PRODUCT_UNIT and main_warehouse["units"] > 0:
                if main_warehouse["units"] >= BATCH_SIZE:
                    units_to_ship = BATCH_SIZE
                else:
                    units_to_ship = main_warehouse["units"]

                current_units += units_to_ship
                main_warehouse["units"] -= units_to_ship
                sub_warehouse["units"] = current_units
                total_units_to_ship += units_to_ship
            if total_units_to_ship > 0:
                report += f"Ship {total_units_to_ship} units of {product} from {main_warehouse['name']} to {sub_warehouse['name']}\n"

    return shipping_db, report.strip()"""

