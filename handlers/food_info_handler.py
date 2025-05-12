from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters
from services.gemini_service import get_food_info

FOOD_NAME = 0

async def start_food_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 What food do you want to learn about?\n(Example: avocado, oatmeal, salmon)")
    return FOOD_NAME

async def receive_food_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    food = update.message.text.strip()
    if not food:
        await update.message.reply_text("⚠️ Please enter a valid food name.")
        return FOOD_NAME

    response = get_food_info(food)
    await update.message.reply_text(response)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Food info request cancelled.")
    return ConversationHandler.END

food_info_handler = ConversationHandler(
    entry_points=[
        CommandHandler("food", start_food_info),
        MessageHandler(filters.Regex("^🥦 Food Info$"), start_food_info)
    ],
    states={
        FOOD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_food_name)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)