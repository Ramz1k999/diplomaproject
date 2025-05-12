from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler,
    ConversationHandler
)

# Define states for text-based conversation
HEIGHT, WEIGHT = range(2)


async def start_water_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        context.user_data["weight"] = weight

        # Create keyboard for activity level
        activity_buttons = [
            [InlineKeyboardButton("Mostly sitting (office work)", callback_data=f"water_activity_sedentary")],
            [InlineKeyboardButton("Light activity (walking)", callback_data=f"water_activity_light")],
            [InlineKeyboardButton("Moderate activity (fast walking)", callback_data=f"water_activity_moderate")],
            [InlineKeyboardButton("Heavy activity (running)", callback_data=f"water_activity_heavy")],
            [InlineKeyboardButton("Athlete level (training)", callback_data=f"water_activity_athlete")]
        ]

        reply_markup = InlineKeyboardMarkup(activity_buttons)
        await update.message.reply_text("🏃‍♂️ What's your typical activity level?", reply_markup=reply_markup)
        return ConversationHandler.END  # End the conversation and let callback handlers take over
    except ValueError:
        await update.message.reply_text("⚠️ Please enter a valid number for weight.")
        return WEIGHT


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Water reminder setup cancelled.")
    return ConversationHandler.END


async def activity_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Parse data
    _, _, activity = query.data.split("_")
    context.user_data["activity"] = activity

    # Create keyboard for climate
    climate_buttons = [
        [InlineKeyboardButton("Cold ❄️", callback_data="water_climate_cold")],
        [InlineKeyboardButton("Temperate 🌤️", callback_data="water_climate_temperate")],
        [InlineKeyboardButton("Hot 🔥", callback_data="water_climate_hot")]
    ]
    reply_markup = InlineKeyboardMarkup(climate_buttons)

    await query.edit_message_text("🌡️ What climate do you live in?", reply_markup=reply_markup)


async def climate_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Parse data
    _, _, climate = query.data.split("_")
    context.user_data["climate"] = climate

    # Calculate personalized water intake
    height = context.user_data.get("height", 170)  # Default if missing
    weight = context.user_data.get("weight", 70)  # Default if missing
    activity = context.user_data.get("activity", "moderate")

    # Calculate water intake
    water_intake_ml = weight * 35  # Base: 35ml per kg

    # Adjust for activity level
    activity_factors = {
        "sedentary": 1.0,
        "light": 1.1,
        "moderate": 1.2,
        "heavy": 1.3,
        "athlete": 1.5
    }
    water_intake_ml *= activity_factors[activity]

    # Adjust for climate
    climate_factors = {
        "cold": 0.9,
        "temperate": 1.0,
        "hot": 1.2
    }
    water_intake_ml *= climate_factors[climate]

    # Convert to liters
    water_intake_liters = water_intake_ml / 1000

    # Create message with recommendations
    activity_descriptions = {
        "sedentary": "Mostly sitting (office work)",
        "light": "Light activity (walking)",
        "moderate": "Moderate activity (fast walking)",
        "heavy": "Heavy activity (running)",
        "athlete": "Athlete level (training)"
    }

    message = f"💧 <b>Your Personalized Water Intake</b>\n\n"
    message += f"Based on your profile:\n"
    message += f"• Height: {height} cm\n"
    message += f"• Weight: {weight} kg\n"
    message += f"• Activity: {activity_descriptions[activity]}\n"
    message += f"• Climate: {climate.capitalize()}\n\n"
    message += f"<b>You should drink approximately {water_intake_liters:.1f} liters of water daily.</b>\n\n"
    message += "This equals to:\n"
    message += f"• {int(water_intake_liters * 4)} glasses (250ml)\n"
    message += f"• {int(water_intake_liters * 1000 / 500)} bottles (500ml)\n\n"
    message += "Would you like me to remind you to drink water throughout the day?"

    # Schedule reminder options
    reminder_buttons = [
        [InlineKeyboardButton("Yes, remind me", callback_data="water_schedule_yes")],
        [InlineKeyboardButton("No, thanks", callback_data="water_schedule_no")]
    ]
    reply_markup = InlineKeyboardMarkup(reminder_buttons)

    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="HTML")


async def schedule_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    choice = query.data.split("_")[2]

    if choice == "yes":
        # In a production system, you would set up actual reminders here
        # using the job queue
        await query.edit_message_text(
            "🔔 <b>Water reminders activated!</b>\n\n"
            "I'll remind you to drink water at these times:\n"
            "• 9:00 AM - Morning hydration\n"
            "• 11:30 AM - Pre-lunch hydration\n"
            "• 2:00 PM - Afternoon refresh\n"
            "• 4:30 PM - End of day hydration\n\n"
            "<i>Pro tip: Try to drink water regularly throughout the day for better hydration.</i>",
            parse_mode="HTML"
        )
    else:
        await query.edit_message_text(
            "👍 <b>Got it! No reminders needed.</b>\n\n"
            "<i>Pro tip: Many people find it helpful to keep a water bottle visible on their desk as a passive reminder to stay hydrated.</i>",
            parse_mode="HTML"
        )


# Create the conversation handler
water_handler = ConversationHandler(
    entry_points=[
        CommandHandler("water", start_water_reminder),
        MessageHandler(filters.Regex("^💧 Water Reminder$"), start_water_reminder)
    ],
    states={
        HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_height)],
        WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_weight)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)


# Function to register all handlers
def register_water_handlers(app):
    # Add the conversation handler
    app.add_handler(water_handler)

    # Add the callback query handlers with namespaced patterns to avoid conflicts
    app.add_handler(CallbackQueryHandler(activity_callback, pattern=r"^water_activity_"))
    app.add_handler(CallbackQueryHandler(climate_callback, pattern=r"^water_climate_"))
    app.add_handler(CallbackQueryHandler(schedule_callback, pattern=r"^water_schedule_"))