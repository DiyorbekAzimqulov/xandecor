# Import State
from aiogram.dispatcher.filters.state import State, StatesGroup

class UserState(StatesGroup):
    categories = State()
    
class SaleVolume(StatesGroup):
    sale_volume = State()