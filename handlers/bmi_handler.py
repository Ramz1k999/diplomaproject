from aiogram import types, Dispatcher
from services.utils import calculate_bmi_info

async def ask_for_bmi_data(message: types.Message):
    await message.reply("Please enter your weight (kg) and height (cm), e.g., `70, 175`")

async def handle_bmi_input(message: types.Message):
    response = calculate_bmi_info(message.text.strip())
    await message.reply(response, parse_mode=types.ParseMode.MARKDOWN)

def register(dp: Dispatcher):
    dp.register_message_handler(ask_for_bmi_data, commands=['bmi'])
    dp.register_message_handler(handle_bmi_input, lambda m: m.reply_to_message and "your weight" in m.reply_to_message.text)
