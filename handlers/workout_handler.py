from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters
from services.gemini_service import generate_workout_plan

# States
ENVIRONMENT, EQUIPMENT, GOAL, FREQUENCY, LIMITATIONS, GENERATE = range(6)


async def start_workout_planner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the workout planner conversation"""

    # Check if we have BMI data
    if "bmi_history" not in context.user_data or not context.user_data["bmi_history"]:
        # No BMI data found
        await update.message.reply_text(
            "⚠️ I don't have your body measurements yet.\n\n"
            "To create a personalized workout plan, I recommend first calculating your BMI.\n"
            "Use the 'BMI & Calories' option first, then come back to the workout planner."
        )

        # Show main menu keyboard
        main_menu_keyboard = [
            ["🧮 BMI & Calories", "💧 Water Reminder"],
            ["🍲 Healthy Recipe", "🥦 Food Info"],
            ["💪 Workout Plan", "◀️ Back"]
        ]
        reply_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)
        await update.message.reply_text("Please calculate your BMI first:", reply_markup=reply_markup)
        return ConversationHandler.END

    # We have BMI data, proceed with workout planner
    latest_bmi = context.user_data["bmi_history"][-1]

    # Store BMI data in workout context
    context.user_data["workout_plan"] = {
        "height": latest_bmi["height"],
        "weight": latest_bmi["weight"],
        "age": latest_bmi["age"],
        "bmi": latest_bmi["bmi"],
        "bmi_category": latest_bmi["category"]
    }

    # Ask about exercise environment
    keyboard = [
        ["🏠 Home", "🏋️ Gym"],
        ["🏞️ Outdoors", "🏢 Office"],
        ["◀️ Back"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🏋️‍♀️ <b>Workout Plan Creator</b>\n\n"
        f"I'll use your measurements (Height: {latest_bmi['height']}cm, Weight: {latest_bmi['weight']}kg, "
        f"BMI: {latest_bmi['bmi']:.1f} - {latest_bmi['category']}) to create a personalized workout plan.\n\n"
        "First, where will you be exercising most often?",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    return ENVIRONMENT


async def receive_environment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store environment and ask about equipment"""

    environment = update.message.text.replace("🏠 ", "").replace("🏋️ ", "").replace("🏞️ ", "").replace("🏢 ", "")
    context.user_data["workout_plan"]["environment"] = environment

    if environment == "Home":
        keyboard = [
            ["No equipment", "Resistance bands"],
            ["Dumbbells", "Full home gym"],
            ["◀️ Back"]
        ]
    elif environment == "Gym":
        keyboard = [
            ["Full access", "Machines only"],
            ["Free weights", "Cardio equipment"],
            ["◀️ Back"]
        ]
    elif environment == "Outdoors":
        keyboard = [
            ["No equipment", "Park with bars"],
            ["Running track", "Hiking trails"],
            ["◀️ Back"]
        ]
    else:  # Office
        keyboard = [
            ["No equipment", "Desk exercises"],
            ["Office chair", "Standing desk"],
            ["◀️ Back"]
        ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "🔧 What equipment do you have access to?",
        reply_markup=reply_markup
    )
    return EQUIPMENT


async def receive_equipment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store equipment and ask about fitness goal"""

    context.user_data["workout_plan"]["equipment"] = update.message.text

    keyboard = [
        ["Lose weight", "Build muscle"],
        ["Improve endurance", "General fitness"],
        ["◀️ Back"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🎯 What's your primary fitness goal?",
        reply_markup=reply_markup
    )
    return GOAL


async def receive_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store goal and ask about frequency"""

    context.user_data["workout_plan"]["goal"] = update.message.text

    keyboard = [
        ["2-3 days/week", "4-5 days/week"],
        ["Every day", "Weekdays only"],
        ["◀️ Back"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "📅 How often can you work out?",
        reply_markup=reply_markup
    )
    return FREQUENCY


async def receive_frequency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store frequency and ask about limitations"""

    context.user_data["workout_plan"]["frequency"] = update.message.text

    keyboard = [
        ["No limitations", "Joint pain"],
        ["Back issues", "Limited mobility"],
        ["◀️ Back"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "⚕️ Do you have any physical limitations or injuries I should consider?",
        reply_markup=reply_markup
    )
    return LIMITATIONS


async def receive_limitations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store limitations and generate workout plan"""

    context.user_data["workout_plan"]["limitations"] = update.message.text

    # Show typing indicator
    await update.message.chat.send_action(action="typing")

    # Inform user we're generating their plan
    await update.message.reply_text(
        "💪 Creating your personalized workout plan...\n"
        "This may take a moment.",
        reply_markup=ReplyKeyboardRemove()
    )

    # Generate workout plan using Gemini
    workout_data = context.user_data["workout_plan"]

    try:
        workout_plan = generate_workout_plan(
            height=workout_data["height"],
            weight=workout_data["weight"],
            age=workout_data["age"],
            bmi=workout_data["bmi"],
            bmi_category=workout_data["bmi_category"],
            environment=workout_data["environment"],
            equipment=workout_data["equipment"],
            goal=workout_data["goal"],
            frequency=workout_data["frequency"],
            limitations=workout_data["limitations"]
        )
    except Exception as e:
        print(f"Error generating workout plan: {e}")
        workout_plan = "I'm sorry, I couldn't generate your workout plan right now. Please try again later."

    # Return to main menu keyboard
    main_menu_keyboard = [
        ["🧮 BMI & Calories", "💧 Water Reminder"],
        ["🍲 Healthy Recipe", "🥦 Food Info"],
        ["💪 Workout Plan", "◀️ Back"]
    ]
    reply_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)

    # Send the workout plan
    await update.message.reply_text(workout_plan, parse_mode="HTML", reply_markup=reply_markup)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the workout planner conversation"""

    main_menu_keyboard = [
        ["🧮 BMI & Calories", "💧 Water Reminder"],
        ["🍲 Healthy Recipe", "🥦 Food Info"],
        ["💪 Workout Plan", "◀️ Back"]
    ]
    reply_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "❌ Workout planning cancelled.",
        reply_markup=reply_markup
    )
    return ConversationHandler.END


# Create the workout planner conversation handler
workout_handler = ConversationHandler(
    entry_points=[
        CommandHandler("workout", start_workout_planner),
        MessageHandler(filters.Regex("^💪 Workout Plan$"), start_workout_planner)
    ],
    states={
        ENVIRONMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_environment)],
        EQUIPMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_equipment)],
        GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_goal)],
        FREQUENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_frequency)],
        LIMITATIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_limitations)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)