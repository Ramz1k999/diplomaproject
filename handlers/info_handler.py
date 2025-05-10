from aiogram import types, Dispatcher
from services.spoonacular import get_product_info

async def ask_product_name(message: types.Message):
    await message.reply("Enter the product name:")

async def handle_product_info(message: types.Message):
    info = get_product_info(message.text.strip())

    if info:
        nutrients = info.get("nutrition", {}).get("nutrients", [])
        response = f"Nutritional info for 100g of {message.text}:\n\n"
        for n in nutrients:
            response += f"{n['name']}: {n['amount']} {n['unit']}\n"
    else:
        response = "Sorry, product not found."

    await message.reply(response)

def register(dp: Dispatcher):
    dp.register_message_handler(ask_product_name, commands=['info'])
    dp.register_message_handler(handle_product_info, lambda m: m.reply_to_message and "Enter the product name" in m.reply_to_message.text)
