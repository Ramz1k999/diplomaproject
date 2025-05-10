from aiogram import types, Dispatcher
from services.spoonacular import get_recipes

async def ask_ingredients(message: types.Message):
    await message.reply("Enter ingredients you have (comma-separated):")

async def handle_ingredient_input(message: types.Message):
    ingredients = [i.strip() for i in message.text.split(',')]
    recipes = get_recipes(ingredients)

    if recipes:
        response = "Here are some recipe suggestions:\n\n"
        for r in recipes:
            title = r['title']
            url = f"https://spoonacular.com/recipes/{title.replace(' ', '-')}-{r['id']}"
            response += f"🍽️ {title}\n🔗 {url}\n\n"
    else:
        response = "Sorry, no recipes found."

    await message.reply(response)

def register(dp: Dispatcher):
    dp.register_message_handler(ask_ingredients, commands=['recipe'])
    dp.register_message_handler(handle_ingredient_input, lambda m: m.reply_to_message and "Enter ingredients" in m.reply_to_message.text)
