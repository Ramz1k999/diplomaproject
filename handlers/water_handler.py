from aiogram import types, Dispatcher
from services.gemini_service import calculate_water_intake

async def ask_for_weight(message: types.Message):
    await message.reply("Please enter your weight in kg:")

async def handle_water_input(message: types.Message):
    response = calculate_water_intake(message.text.strip())
    await message.reply(response, parse_mode=types.ParseMode.MARKDOWN)

def register(dp: Dispatcher):
    dp.register_message_handler(ask_for_weight, commands=['water'])
    dp.register_message_handler(handle_water_input, lambda m: m.reply_to_message and "your weight in kg" in m.reply_to_message.text)
