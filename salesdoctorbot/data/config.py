from environs import Env

# environs kutubxonasidan foydalanish
env = Env()
env.read_env()

# .env fayl ichidan quyidagilarni o'qiymiz
BOT_TOKEN = env.str("BOT_TOKEN3")  # Bot toekn
ADMINS = env.list("ADMINS")  # adminlar ro'yxati
GROUP_ID = env.int("GROUP_ID")  # guruh id raqami
CATEGORY_ID = "d0_5"
