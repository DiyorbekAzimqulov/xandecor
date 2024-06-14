import asyncio
from aiogram import executor
from loader import dp
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from salebot.utils.db_api.time_management import notify_users_deadline

async def on_startup(dispatcher):
    print("bot started")
    await set_default_commands(dispatcher)
    print("Commands set")
    asyncio.create_task(notify_users_deadline())
    await on_startup_notify(dispatcher)
    print("Admin notified")

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
