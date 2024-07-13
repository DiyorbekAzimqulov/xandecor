import asyncio

from aiogram import executor

from loader import dp


import middlewares, filters, handlers
from utils.db_api.cron import daily_shipping_report, daily_redistribute_report
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    print("bot started")
    # Birlamchi komandalar (/star va /help)
    await set_default_commands(dispatcher)
    print("Commands set")
    print("Daily shipping report started")
    asyncio.create_task(daily_shipping_report())
    print("Daily shipping report finished")
    print("Daily redistribute started")
    asyncio.create_task(daily_redistribute_report())
    print("Daily redistribute finished")
    # Bot ishga tushgani haqida adminga xabar berish
    await on_startup_notify(dispatcher)


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
