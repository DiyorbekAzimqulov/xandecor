import asyncio
from aiogram import executor
from loader import dp
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
scheduler = AsyncIOScheduler()


async def on_startup(dispatcher):
    print("Bot started")
    # Set initial commands (/start and /help)
    await set_default_commands(dispatcher)
    
    print("Commands set")
    # Notify admin on bot startup
    await on_startup_notify(dispatcher)

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
