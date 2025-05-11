from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! I'm your personal health assistant bot.\n\n"
        "You can use these commands:\n"
        "• /bmi - Check your BMI & get water recommendation\n"
        "• /recipe - Get a healthy recipe using your ingredients\n"
        "• /food - Get info about a food item\n"
        "• /cancel - Cancel any operation"
    )

help_command = CommandHandler("start", start)
