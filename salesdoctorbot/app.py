import asyncio

from aiogram import executor

from loader import dp


import middlewares, filters, handlers
from utils.db_api.cron import daily_shipping_report, daily_redistribute_report, daily_forgotten_shipments
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    print("Bot started")
    # Set initial commands (/start and /help)
    await set_default_commands(dispatcher)
    print("Commands set")

    # Start daily shipping report task
    try:
        asyncio.create_task(daily_shipping_report())
        print("Daily shipping report task created")
    except Exception as e:
        print(f"Error creating daily shipping report task: {e}")

    # Start daily redistribute report task
    try:
        asyncio.create_task(daily_redistribute_report())
        print("Daily redistribute report task created")
    except Exception as e:
        print(f"Error creating daily redistribute report task: {e}")

    # Start daily forgotten shipments task
    try:
        asyncio.create_task(daily_forgotten_shipments())
        print("Daily forgotten shipments task created")
    except Exception as e:
        print(f"Error creating daily forgotten shipments task: {e}")

    # Notify admin on bot startup
    await on_startup_notify(dispatcher)

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
