from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters
from services.gemini_service import handle_bmi_with_gemini, get_water_reminder

HEIGHT, WEIGHT, AGE, OCCUPATION = range(4)

async def start_bmi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📏 Please enter your height in cm (e.g. 170):")
    return HEIGHT

async def receive_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["height"] = int(update.message.text)
        await update.message.reply_text("⚖️ Now enter your weight in kg (e.g. 65):")
        return WEIGHT
    except ValueError:
        await update.message.reply_text("⚠️ Please enter valid number for height.")
        return HEIGHT

async def receive_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["weight"] = int(update.message.text)
        await update.message.reply_text("🎂 How old are you?")
        return AGE
    except ValueError:
        await update.message.reply_text("⚠️ Please enter a valid number for weight.")
        return WEIGHT

async def receive_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["age"] = int(update.message.text)
        await update.message.reply_text("💼 What is your occupation?")
        return OCCUPATION
    except ValueError:
        await update.message.reply_text("⚠️ Please enter a valid number for age.")
        return AGE

async def receive_occupation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["occupation"] = update.message.text

    height = context.user_data["height"]
    weight = context.user_data["weight"]
    age = context.user_data["age"]
    occupation = context.user_data["occupation"]

    bmi_response = handle_bmi_with_gemini(height, weight, age, occupation)
    water_reminder = get_water_reminder(height, weight)

    await update.message.reply_text(f"{bmi_response}\n\n{water_reminder}")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ BMI check cancelled.")
    return ConversationHandler.END

bmi_handler = ConversationHandler(
    entry_points=[
        CommandHandler("bmi", start_bmi),
        MessageHandler(filters.Regex("^🧮 BMI & Calories$"), start_bmi)
    ],
    states={
        HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_height)],
        WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_weight)],
        AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_age)],
        OCCUPATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_occupation)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)