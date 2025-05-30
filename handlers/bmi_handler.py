from telegram import Update, ReplyKeyboardMarkup
from datetime import datetime
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters
from services.gemini_service import handle_bmi_with_gemini, get_water_reminder

HEIGHT, WEIGHT, AGE, OCCUPATION, BMI_OPTION = range(5)


async def start_bmi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check for previous BMI history
    if "bmi_history" in context.user_data and context.user_data["bmi_history"]:
        # Get most recent calculation
        latest = context.user_data["bmi_history"][-1]

        await update.message.reply_text(
            f"💾 <b>Your Latest BMI Result</b>\n\n"
            f"Date: {latest['date']}\n"
            f"Height: {latest['height']} cm\n"
            f"Weight: {latest['weight']} kg\n"
            f"Age: {latest['age']} years\n"
            f"BMI: {latest['bmi']:.1f} ({latest['category']})\n\n"
            f"Would you like to calculate a new BMI or continue with these values?",
            parse_mode="HTML"
        )

        # Give option to use previous values or start new calculation
        keyboard = [
            ["📊 New Calculation", "📈 Use Previous Values"],
            ["◀️ Back"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Select an option:", reply_markup=reply_markup)
        return BMI_OPTION

    # No history, start normal flow
    await update.message.reply_text("📏 Please enter your height in cm (e.g. 170):")
    return HEIGHT


async def handle_bmi_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    option = update.message.text

    if option == "📊 New Calculation":
        await update.message.reply_text("📏 Please enter your height in cm (e.g. 170):")
        return HEIGHT

    elif option == "📈 Use Previous Values":
        # Get most recent values
        latest = context.user_data["bmi_history"][-1]

        # Pre-fill the values
        context.user_data["height"] = latest["height"]
        context.user_data["weight"] = latest["weight"]
        context.user_data["age"] = latest["age"]

        # Skip to occupation since other values are reused
        await update.message.reply_text(
            f"Using your previous values:\n"
            f"• Height: {latest['height']} cm\n"
            f"• Weight: {latest['weight']} kg\n"
            f"• Age: {latest['age']} years\n\n"
            f"💼 What is your occupation or activity level currently?"
        )
        return OCCUPATION

    elif option == "◀️ Back":
        # Return to main menu
        main_menu_keyboard = [
            ["🧮 BMI & Calories", "💧 Water Reminder"],
            ["🍲 Healthy Recipe", "🥦 Food Info"],
            ["💪 Workout Plan", "◀️ Back"]
        ]
        reply_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)
        await update.message.reply_text("Returning to main menu.", reply_markup=reply_markup)
        return ConversationHandler.END

    # If we reach here, it's an unrecognized option
    await update.message.reply_text("Please select one of the available options.")
    return BMI_OPTION


async def receive_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "◀️ Back":
        # Return to main menu
        main_menu_keyboard = [
            ["🧮 BMI & Calories", "💧 Water Reminder"],
            ["🍲 Healthy Recipe", "🥦 Food Info"],
            ["💪 Workout Plan", "◀️ Back"]
        ]
        reply_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)
        await update.message.reply_text("Returning to main menu.", reply_markup=reply_markup)
        return ConversationHandler.END

    try:
        height = int(text)
        if height < 50 or height > 250:
            await update.message.reply_text("⚠️ Please enter a valid height between 50 and 250 cm.")
            return HEIGHT

        context.user_data["height"] = height
        await update.message.reply_text("⚖️ Now enter your weight in kg (e.g. 65):")
        return WEIGHT
    except ValueError:
        await update.message.reply_text("⚠️ Please enter a valid number for height.")
        return HEIGHT


async def receive_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "◀️ Back":
        # Return to main menu
        main_menu_keyboard = [
            ["🧮 BMI & Calories", "💧 Water Reminder"],
            ["🍲 Healthy Recipe", "🥦 Food Info"],
            ["💪 Workout Plan", "◀️ Back"]
        ]
        reply_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)
        await update.message.reply_text("Returning to main menu.", reply_markup=reply_markup)
        return ConversationHandler.END

    try:
        weight = int(text)
        if weight < 20 or weight > 300:
            await update.message.reply_text("⚠️ Please enter a valid weight between 20 and 300 kg.")
            return WEIGHT

        context.user_data["weight"] = weight
        await update.message.reply_text("🎂 How old are you?")
        return AGE
    except ValueError:
        await update.message.reply_text("⚠️ Please enter a valid number for weight.")
        return WEIGHT


async def receive_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "◀️ Back":
        # Return to main menu
        main_menu_keyboard = [
            ["🧮 BMI & Calories", "💧 Water Reminder"],
            ["🍲 Healthy Recipe", "🥦 Food Info"],
            ["💪 Workout Plan", "◀️ Back"]
        ]
        reply_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)
        await update.message.reply_text("Returning to main menu.", reply_markup=reply_markup)
        return ConversationHandler.END

    try:
        age = int(text)
        if age < 1 or age > 120:
            await update.message.reply_text("⚠️ Please enter a valid age between 1 and 120 years.")
            return AGE

        context.user_data["age"] = age
        await update.message.reply_text("💼 What is your occupation or activity level?")
        return OCCUPATION
    except ValueError:
        await update.message.reply_text("⚠️ Please enter a valid number for age.")
        return AGE


async def receive_occupation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "◀️ Back":
        # Return to main menu
        main_menu_keyboard = [
            ["🧮 BMI & Calories", "💧 Water Reminder"],
            ["🍲 Healthy Recipe", "🥦 Food Info"],
            ["💪 Workout Plan", "◀️ Back"]
        ]
        reply_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)
        await update.message.reply_text("Returning to main menu.", reply_markup=reply_markup)
        return ConversationHandler.END

    context.user_data["occupation"] = text

    height = context.user_data["height"]
    weight = context.user_data["weight"]
    age = context.user_data["age"]
    occupation = context.user_data["occupation"]

    # Calculate basic BMI for storage
    height_m = height / 100
    bmi = weight / (height_m * height_m)

    # Determine BMI category
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obesity"

    # Create BMI history object
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    bmi_entry = {
        "date": date_str,
        "height": height,
        "weight": weight,
        "age": age,
        "occupation": occupation,
        "bmi": bmi,
        "category": category
    }

    # Store in user history
    if "bmi_history" not in context.user_data:
        context.user_data["bmi_history"] = []
    context.user_data["bmi_history"].append(bmi_entry)

    # Get full responses
    bmi_response = handle_bmi_with_gemini(height, weight, age, occupation)
    water_reminder = get_water_reminder(height, weight)

    # Show main menu keyboard after results
    main_menu_keyboard = [
        ["🧮 BMI & Calories", "💧 Water Reminder"],
        ["🍲 Healthy Recipe", "🥦 Food Info"],
        ["💪 Workout Plan", "◀️ Back"]
    ]
    reply_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)

    await update.message.reply_text(f"{bmi_response}\n\n{water_reminder}", reply_markup=reply_markup)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation but preserve user data"""
    # Return to main menu
    main_menu_keyboard = [
        ["🧮 BMI & Calories", "💧 Water Reminder"],
        ["🍲 Healthy Recipe", "🥦 Food Info"],
        ["💪 Workout Plan", "◀️ Back"]
    ]
    reply_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)
    await update.message.reply_text("Operation cancelled. Returning to main menu.", reply_markup=reply_markup)
    return ConversationHandler.END


# Create the conversation handler with direct back button handling
bmi_handler = ConversationHandler(
    entry_points=[
        CommandHandler("bmi", start_bmi),
        MessageHandler(filters.Regex("^🧮 BMI & Calories$"), start_bmi)
    ],
    states={
        BMI_OPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bmi_option)],
        HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_height)],
        WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_weight)],
        AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_age)],
        OCCUPATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_occupation)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    name="bmi_conversation",  # Give the handler a name
    allow_reentry=True  # Allow re-entering the conversation
)