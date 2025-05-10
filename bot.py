from aiogram import Bot, Dispatcher, executor
from config import TELEGRAM_API_TOKEN
from handlers import start_handler, lang_handler, bmi_handler, water_handler, recipe_handler, info_handler

bot = Bot(token=TELEGRAM_API_TOKEN)
dp = Dispatcher(bot)

# Register all handlers
lang_handler.register(dp)
start_handler.register(dp)
bmi_handler.register(dp)
water_handler.register(dp)
recipe_handler.register(dp)
info_handler.register(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
