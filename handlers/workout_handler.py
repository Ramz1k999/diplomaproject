from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters
from services.gemini_service import generate_workout_plan
from datetime import datetime

# Conversation states
CHOOSE_ACTION, ENVIRONMENT, EQUIPMENT, GOAL, FREQUENCY, LIMITATIONS = range(6)

# Constants for reused messages and keyboards
MAIN_MENU_KEYBOARD = [
    ["🧮 BMI & Calories", "💧 Water Reminder"],
    ["🍲 Healthy Recipe", "🥦 Food Info"],
    ["💪 Workout Plan", "◀️ Back"]
]

# Keyboard options based on environment
EQUIPMENT_OPTIONS = {
    "Home": [
        ["No equipment", "Resistance bands"],
        ["Dumbbells", "Full home gym"],
        ["◀️ Back"]
    ],
    "Gym": [
        ["Full access", "Machines only"],
        ["Free weights", "Cardio equipment"],
        ["◀️ Back"]
    ],
    "Outdoors": [
        ["No equipment", "Park with bars"],
        ["Running track", "Hiking trails"],
        ["◀️ Back"]
    ],
    "Office": [
        ["No equipment", "Resistance bands"],
        ["Small dumbbells", "Exercise ball"],
        ["◀️ Back"]
    ]
}


# Helper functions
def get_main_menu_markup():
    """Return main menu keyboard markup"""
    return ReplyKeyboardMarkup(MAIN_MENU_KEYBOARD, resize_keyboard=True)


async def return_to_main_menu(update: Update):
    """Helper to return to main menu"""
    await update.message.reply_text("Returning to main menu.", reply_markup=get_main_menu_markup())
    return ConversationHandler.END


# Main conversation handlers
async def start_workout_planner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Entry point: Show existing plan or start creating a new one"""

    # Check if user has an existing plan
    if "workout_plan" in context.user_data and "plan_text" in context.user_data["workout_plan"]:
        plan = context.user_data["workout_plan"]
        created_date = plan.get("created_date", "Unknown date")

        # Display plan summary
        summary = (
            f"💪 <b>Your Current Workout Plan</b>\n\n"
            f"Created on: {created_date}\n"
            f"Environment: {plan.get('environment', 'Not specified')}\n"
            f"Goal: {plan.get('goal', 'Not specified')}\n"
            f"Frequency: {plan.get('frequency', 'Not specified')}\n\n"
        )

        await update.message.reply_text(summary, parse_mode="HTML")

        # Show options for existing plan
        keyboard = [
            ["👁️ View Current Plan", "🔄 Create New Plan"],
            ["◀️ Back"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("What would you like to do?", reply_markup=reply_markup)
        return CHOOSE_ACTION

    # No existing plan, check if BMI data exists
    if "bmi_history" not in context.user_data or not context.user_data["bmi_history"]:
        await update.message.reply_text(
            "⚠️ I don't have your body measurements yet.\n\n"
            "To create a personalized workout plan, I recommend first calculating your BMI.\n"
            "Use the 'BMI & Calories' option first, then come back to the workout planner.",
            reply_markup=get_main_menu_markup()
        )
        return ConversationHandler.END

    # We have BMI data, proceed to create a new plan
    return await start_new_plan(update, context)


async def handle_workout_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process user's choice about existing workout plan"""
    choice = update.message.text

    if choice == "👁️ View Current Plan":
        if "workout_plan" in context.user_data and "plan_text" in context.user_data["workout_plan"]:
            # Send the saved plan and return to main menu
            await update.message.reply_text(
                context.user_data["workout_plan"]["plan_text"],
                parse_mode="HTML",
                reply_markup=get_main_menu_markup()
            )
            return ConversationHandler.END

    elif choice == "🔄 Create New Plan":
        return await start_new_plan(update, context)

    elif choice == "◀️ Back":
        return await return_to_main_menu(update)

    # Unrecognized option
    await update.message.reply_text("Please select one of the available options.")
    return CHOOSE_ACTION


async def start_new_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the process of creating a new workout plan"""
    # Get latest BMI data
    latest_bmi = context.user_data["bmi_history"][-1]

    # Initialize workout plan data structure
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
    """Handle environment selection and request equipment info"""
    text = update.message.text

    if text == "◀️ Back":
        return await return_to_main_menu(update)

    # Clean up the input by removing emojis
    environment = text.replace("🏠 ", "").replace("🏋️ ", "").replace("🏞️ ", "").replace("🏢 ", "")
    context.user_data["workout_plan"]["environment"] = environment

    # Get the appropriate keyboard options for this environment
    keyboard = EQUIPMENT_OPTIONS.get(environment, EQUIPMENT_OPTIONS["Home"])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🔧 What equipment do you have access to?",
        reply_markup=reply_markup
    )
    return EQUIPMENT


async def receive_equipment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle equipment selection and ask about fitness goals"""
    text = update.message.text

    if text == "◀️ Back":
        return await return_to_main_menu(update)

    context.user_data["workout_plan"]["equipment"] = text

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
    """Handle goal selection and ask about workout frequency"""
    text = update.message.text

    if text == "◀️ Back":
        return await return_to_main_menu(update)

    context.user_data["workout_plan"]["goal"] = text

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
    """Handle frequency selection and ask about physical limitations"""
    text = update.message.text

    if text == "◀️ Back":
        return await return_to_main_menu(update)

    context.user_data["workout_plan"]["frequency"] = text

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
    """Generate workout plan based on all collected information"""
    text = update.message.text

    if text == "◀️ Back":
        return await return_to_main_menu(update)

    context.user_data["workout_plan"]["limitations"] = text

    # Show typing indicator
    await update.message.chat.send_action(action="typing")

    # Inform user we're generating their plan
    await update.message.reply_text(
        "💪 Creating your personalized workout plan...\n"
        "This may take a moment.",
        reply_markup=ReplyKeyboardRemove()
    )

    try:
        # Generate workout plan using all the collected data
        workout_data = context.user_data["workout_plan"]
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

        # Save the generated plan and timestamp
        context.user_data["workout_plan"]["plan_text"] = workout_plan
        context.user_data["workout_plan"]["created_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Add confirmation message
        success_message = (
            f"{workout_plan}\n\n"
            f"<i>✅ Your workout plan has been saved. You can access it anytime "
            f"by selecting 'Workout Plan' from the menu.</i>"
        )

    except Exception as e:
        print(f"Error generating workout plan: {e}")
        success_message = (
            "❌ I'm sorry, I couldn't generate your workout plan right now. "
            "Please try again later."
        )

    # Send the workout plan and return to main menu
    await update.message.reply_text(
        success_message,
        parse_mode="HTML",
        reply_markup=get_main_menu_markup()
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle explicit cancellation"""
    await update.message.reply_text(
        "❌ Workout planning cancelled.",
        reply_markup=get_main_menu_markup()
    )
    return ConversationHandler.END


# Create the workout planner conversation handler
workout_handler = ConversationHandler(
    entry_points=[
        CommandHandler("workout", start_workout_planner),
        MessageHandler(filters.Regex("^💪 Workout Plan$"), start_workout_planner)
    ],
    states={
        CHOOSE_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_workout_action)],
        ENVIRONMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_environment)],
        EQUIPMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_equipment)],
        GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_goal)],
        FREQUENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_frequency)],
        LIMITATIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_limitations)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    name="workout_conversation",  # Named conversation for better debugging
    allow_reentry=True  # Allow users to restart the conversation
)