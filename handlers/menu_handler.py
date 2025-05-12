from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

# Import the entry point functions from your handlers
from handlers.bmi_handler import start_bmi
from handlers.food_info_handler import start_food_info
from handlers.recipe_handler import start_recipe
from services.gemini_service import get_water_reminder


async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🧮 BMI & Calories":
        return await start_bmi(update, context)
    elif text == "💧 Water Reminder":
        await update.message.reply_text("Please enter your weight in kg:")
        context.user_data["waiting_for_water_weight"] = True
    elif text == "🍲 Healthy Recipe":
        return await start_recipe(update, context)
    elif text == "🥦 Food Info":
        return await start_food_info(update, context)
    elif text == "❌ Cancel":
        await update.message.reply_text("Operation cancelled. What else would you like to do?")


# Add a handler for the water weight input
async def handle_water_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "waiting_for_water_weight" in context.user_data and context.user_data["waiting_for_water_weight"]:
        try:
            weight = float(update.message.text.strip())
            water_reminder = get_water_reminder(170, weight)  # Using default height
            await update.message.reply_text(water_reminder)
            context.user_data["waiting_for_water_weight"] = False
        except ValueError:
            await update.message.reply_text("⚠️ Please enter a valid weight.")


menu_handler = MessageHandler(
    filters.TEXT & ~filters.COMMAND &
    filters.Regex("^(🧮 BMI & Calories|💧 Water Reminder|🍲 Healthy Recipe|🥦 Food Info|❌ Cancel)$"),
    handle_menu_selection
)

water_weight_handler = MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    handle_water_weight
)