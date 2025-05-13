from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

# Import the entry point functions from your handlers
from handlers.bmi_handler import start_bmi
from handlers.food_info_handler import start_food_info
from handlers.help_handler import clear_chat
from handlers.recipe_handler import start_recipe
from handlers.water_handler import start_water_reminder


async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🧮 BMI & Calories":
        return await start_bmi(update, context)
    elif text == "💧 Water Reminder":
        return await start_water_reminder(update, context)
    elif text == "🍲 Healthy Recipe":
        return await start_recipe(update, context)
    elif text == "🥦 Food Info":
        return await start_food_info(update, context)
    elif text == "◀️ Back":
        return await clear_chat(update, context)



menu_handler = MessageHandler(
    filters.TEXT & ~filters.COMMAND &
    filters.Regex("^(🧮 BMI & Calories|💧 Water Reminder|🍲 Healthy Recipe|🥦 Food Info|🔄 Clear Chat)$"),
    handle_menu_selection
)
