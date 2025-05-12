from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters
from services.gemini_service import get_water_reminder

# Define conversation states
HEIGHT, WEIGHT = range(2)


async def start_water_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📏 Please enter your height in cm (e.g. 170):")
    return HEIGHT


async def receive_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["height"] = int(update.message.text)
        await update.message.reply_text("⚖️ Now enter your weight in kg (e.g. 65):")
        return WEIGHT
    except ValueError:
        await update.message.reply_text("⚠️ Please enter a valid number for height.")
        return HEIGHT


async def receive_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        height = context.user_data["height"]
        weight = int(update.message.text)

        water_reminder = get_water_reminder(height, weight)
        await update.message.reply_text(water_reminder)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("⚠️ Please enter a valid number for weight.")
        return WEIGHT


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Water reminder cancelled.")
    return ConversationHandler.END


water_handler = ConversationHandler(
    entry_points=[
        CommandHandler("water", start_water_reminder),
        MessageHandler(filters.Regex("^💧 Water Reminder$"), start_water_reminder)
    ],
    states={
        HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_height)],
        WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_weight)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)