from aiogram import types
from salesdoctorbot.models import WareHouse
from asgiref.sync import sync_to_async

async def set_default_commands(dp):
    warehouses = await sync_to_async(lambda: list(WareHouse.objects.exclude(name="Основной склад")))()
    
    # List to store the commands
    commands = [
        types.BotCommand("start", "Botni ishga tushurish"),
        types.BotCommand("help", "Yordam"),
    ]
    
    # Add a command for each warehouse
    for warehouse in warehouses:
        commands.append(types.BotCommand(f"warehouse_{warehouse.id}", f"{warehouse.name} ombori haqida ma'lumot olish"))

    # Set the commands for the bot
    await dp.bot.set_my_commands(commands)
