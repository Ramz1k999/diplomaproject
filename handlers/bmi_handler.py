from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters
from services.gemini_service import handle_bmi_with_gemini, get_water_reminder

HEIGHT, WEIGHT = range(2)

async def start_bmi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📏 Please enter your height in cm (e.g. 170):")
    return HEIGHT

async def receive_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        height = int(update.message.text)
        context.user_data["height"] = height
        await update.message.reply_text("⚖️ Now enter your weight in kg (e.g. 65):")
        return WEIGHT
    except ValueError:
        await update.message.reply_text("⚠️ Please enter a valid number for height.")
        return HEIGHT

async def receive_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        weight = int(update.message.text)
        height = context.user_data["height"]

        bmi_response = handle_bmi_with_gemini(height, weight)
        water_reminder = get_water_reminder(height, weight)

        await update.message.reply_text(f"{bmi_response}\n\n{water_reminder}")
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("⚠️ Please enter a valid number for weight.")
        return WEIGHT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ BMI check cancelled.")
    return ConversationHandler.END

bmi_handler = ConversationHandler(
    entry_points=[CommandHandler("bmi", start_bmi)],
    states={
        HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_height)],
        WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_weight)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
