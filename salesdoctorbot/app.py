import asyncio

from aiogram import executor

from loader import dp
import middlewares, filters, handlers
from utils.db_api.cron import generate_daily_report
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    print("bot started")
    # Birlamchi komandalar (/star va /help)
    await set_default_commands(dispatcher)
    print("Commands set")
    asyncio.create_task(generate_daily_report())
    # Bot ishga tushgani haqida adminga xabar berish
    await on_startup_notify(dispatcher)


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
