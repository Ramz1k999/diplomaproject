from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes

main_menu_keyboard = [
    ["🧮 BMI & Calories", "💧 Water Reminder"],
    ["🍲 Healthy Recipe", "🥦 Food Info"],
    ["❌ Cancel"]
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    main_menu_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "👋 Hello! I'm your personal health assistant bot.\n\n"
        "You can use these commands:\n"
        "• /bmi - Check your BMI & get water recommendation\n"
        "• /recipe - Get a healthy recipe using your ingredients\n"
        "• /food - Get info about a food item\n"
        "• /cancel - Cancel any operation",
        reply_markup=main_menu_markup
    )

help_command = CommandHandler("start", start)