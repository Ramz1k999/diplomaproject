from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes
from services.gemini_service import get_random_health_tip

# Enhanced keyboard with better organization
main_menu_keyboard = [
    ["🧮 BMI & Calories", "💧 Water Reminder"],
    ["🍲 Healthy Recipe", "🥦 Food Info"],
    ["◀️ Back"]
]



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if context.user_data:
        context.user_data.clear()

    # Get user's first name if available
    user_first_name = update.effective_user.first_name if update.effective_user else "there"


    # Show typing indicator while getting the health tip
    await update.message.chat.send_action(action="typing")

    # Get a fresh health tip from Gemini
    daily_tip = get_random_health_tip()

    main_menu_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)

    welcome_message = (
        f"👋 <b>Hello, {user_first_name}!</b>\n\n"
        f"I'm your personal health assistant bot designed to help you make better health choices.\n\n"
        f"<b>💡 Daily Health Tip:</b> <i>{daily_tip}</i>\n\n"
        f"<b>What I can do for you:</b>\n\n"
        f"• <b>🧮 BMI & Calories</b> - Calculate your BMI, daily calorie needs, and get personalized health insights\n\n"
        f"• <b>💧 Water Reminder</b> - Get personalized hydration recommendations based on your profile\n\n"
        f"• <b>🍲 Healthy Recipe</b> - Discover delicious, healthy recipes using ingredients you already have\n\n"
        f"• <b>🥦 Food Info</b> - Learn detailed nutritional information about any food\n\n"
        f"<b>How to use:</b> Simply tap one of the buttons below or use the corresponding commands (/bmi, /water, /recipe, /food)\n\n"
        f"<i>This assistant is designed to provide general health information and is not a substitute for professional medical advice.</i>"
    )

    await update.message.reply_text(welcome_message, reply_markup=main_menu_markup, parse_mode="HTML")

async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear all user data and restart the conversation"""
    # Call the start function to show the welcome message and reset everything
    return await start(update, context)


help_command = CommandHandler("start", start)
