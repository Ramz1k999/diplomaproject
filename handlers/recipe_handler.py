from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters
from services.gemini_service import get_healthy_recipe

INGREDIENTS = 0


async def start_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🍅 Please enter the ingredients you have, separated by commas.\n"
        "Example: chicken, broccoli, garlic"
    )
    return INGREDIENTS


async def receive_ingredients(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    ingredients = [i.strip() for i in text.split(",") if i.strip()]

    if not ingredients:
        await update.message.reply_text("⚠️ Please enter at least one ingredient.")
        return INGREDIENTS

    response = get_healthy_recipe(ingredients)
    await update.message.reply_text(response)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Recipe request cancelled.")
    return ConversationHandler.END


recipe_handler = ConversationHandler(
    entry_points=[
        CommandHandler("recipe", start_recipe),
        MessageHandler(filters.Regex("^🍲 Healthy Recipe$"), start_recipe)
    ],
    states={
        INGREDIENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_ingredients)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)