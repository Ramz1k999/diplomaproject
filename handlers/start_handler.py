from aiogram import types, Dispatcher
from handlers.lang_handler import get_text

async def send_welcome(message: types.Message):
    text = get_text(message.from_user.id, "start")
    await message.answer(text, parse_mode=types.ParseMode.MARKDOWN)

def register(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start'])
