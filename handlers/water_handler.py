from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler,
    ConversationHandler
)
from datetime import datetime, time as datetime_time

# Define states for conversation
HEIGHT, WEIGHT = range(2)

# Job name pattern for water reminders
JOB_NAME_PREFIX = "water_reminder_"


async def start_water_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the water reminder setup process or show existing settings"""

    # Check if user already has water settings configured
    if "water_settings" in context.user_data and "daily_intake_liters" in context.user_data["water_settings"]:
        # User has existing water settings
        settings = context.user_data["water_settings"]

        # Create message with existing settings
        message = f"💧 <b>Your Water Settings</b>\n\n"
        message += f"• Daily intake: {settings['daily_intake_liters']:.1f} liters\n"

        if "reminder_hours" in settings:
            if settings["reminder_hours"] == 0:
                message += "• Reminders: None\n"
            else:
                message += f"• Reminders: Every {settings['reminder_hours']} hour(s)\n"
                if "reminder_start_hour" in settings and "reminder_end_hour" in settings:
                    message += f"• Active hours: {settings['reminder_start_hour']}:00 to {settings['reminder_end_hour']}:00\n"

        message += "\nWhat would you like to do?"

        # Create keyboard for options
        buttons = [
            [InlineKeyboardButton("📋 View Schedule", callback_data="water_view_schedule")],
            [InlineKeyboardButton("✅ Log Water Intake", callback_data="water_checkin")],
            [InlineKeyboardButton("🔄 Create New Water Plan", callback_data="water_new_plan")],
            [InlineKeyboardButton("🗑️ Reset Today's Check-ins", callback_data="water_reset_checkins")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(message, parse_mode="HTML", reply_markup=reply_markup)
        return ConversationHandler.END

    # Check if we already have BMI data (for new users)
    if "bmi_history" in context.user_data and context.user_data["bmi_history"]:
        # Use the most recent BMI data
        latest_bmi = context.user_data["bmi_history"][-1]
        height = latest_bmi["height"]
        weight = latest_bmi["weight"]

        # Store in water settings
        context.user_data["water_settings"] = {"height": height, "weight": weight}

        await update.message.reply_text(
            f"📊 <b>Using your existing profile data:</b>\n"
            f"• Height: {height} cm\n"
            f"• Weight: {weight} kg\n\n"
            f"This will help calculate your ideal water intake.",
            parse_mode="HTML"
        )

        # Skip directly to activity level
        activity_buttons = [
            [InlineKeyboardButton("Mostly sitting (office work)", callback_data="water_activity_sedentary")],
            [InlineKeyboardButton("Light activity (walking)", callback_data="water_activity_light")],
            [InlineKeyboardButton("Moderate activity (fast walking)", callback_data="water_activity_moderate")],
            [InlineKeyboardButton("Heavy activity (running)", callback_data="water_activity_heavy")],
            [InlineKeyboardButton("Athlete level (training)", callback_data="water_activity_athlete")]
        ]
        reply_markup = InlineKeyboardMarkup(activity_buttons)

        await update.message.reply_text(
            "🏃‍♂️ What's your typical activity level?",
            reply_markup=reply_markup
        )

        # End the text conversation since we're switching to inline buttons
        return ConversationHandler.END

    # If we get here, we don't have BMI data or existing water settings
    await update.message.reply_text("📏 Please enter your height in cm (e.g. 170):")
    return HEIGHT


async def new_plan_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start creating a new water plan"""
    query = update.callback_query
    await query.answer()

    # Check for BMI data
    if "bmi_history" in context.user_data and context.user_data["bmi_history"]:
        latest_bmi = context.user_data["bmi_history"][-1]
        height = latest_bmi["height"]
        weight = latest_bmi["weight"]

        # Reset water settings while keeping history but clearing today's check-ins
        water_checkins = context.user_data.get("water_checkins", [])
        now = datetime.now()
        today = now.date()

        # Filter out today's check-ins while preserving history
        water_checkins = [c for c in water_checkins
                          if datetime.strptime(c["timestamp"], "%Y-%m-%d %H:%M").date() != today]

        context.user_data["water_settings"] = {"height": height, "weight": weight}
        context.user_data["water_checkins"] = water_checkins

        await query.message.reply_text(
            f"📊 <b>Using your existing profile data:</b>\n"
            f"• Height: {height} cm\n"
            f"• Weight: {weight} kg\n\n"
            f"Let's create a new water plan for you.",
            parse_mode="HTML"
        )

        # Skip to activity level
        activity_buttons = [
            [InlineKeyboardButton("Mostly sitting (office work)", callback_data="water_activity_sedentary")],
            [InlineKeyboardButton("Light activity (walking)", callback_data="water_activity_light")],
            [InlineKeyboardButton("Moderate activity (fast walking)", callback_data="water_activity_moderate")],
            [InlineKeyboardButton("Heavy activity (running)", callback_data="water_activity_heavy")],
            [InlineKeyboardButton("Athlete level (training)", callback_data="water_activity_athlete")]
        ]
        reply_markup = InlineKeyboardMarkup(activity_buttons)

        await query.message.reply_text("🏃‍♂️ What's your typical activity level?", reply_markup=reply_markup)
        return

    # No BMI data, start from beginning
    await query.message.reply_text("Let's create a new water plan for you! First, I need some information.")
    await query.message.reply_text("📏 Please enter your height in cm (e.g. 170):")

    # Reset water settings and clear today's check-ins
    water_checkins = context.user_data.get("water_checkins", [])
    now = datetime.now()
    today = now.date()

    # Filter out today's check-ins while preserving history
    water_checkins = [c for c in water_checkins
                      if datetime.strptime(c["timestamp"], "%Y-%m-%d %H:%M").date() != today]

    if "water_settings" in context.user_data:
        del context.user_data["water_settings"]
    context.user_data["water_checkins"] = water_checkins

    # Start the conversation handler with HEIGHT state
    return HEIGHT


async def reset_checkins_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset water check-ins for the current day"""
    query = update.callback_query
    await query.answer("Resetting today's water check-ins...")

    # Get current date
    now = datetime.now()
    today = now.date()

    # Initialize checkin history if needed
    if "water_checkins" not in context.user_data:
        context.user_data["water_checkins"] = []

    # Filter out today's check-ins while preserving history
    water_checkins = context.user_data["water_checkins"]
    water_checkins = [c for c in water_checkins
                      if datetime.strptime(c["timestamp"], "%Y-%m-%d %H:%M").date() != today]

    # Save the filtered check-ins back to user data
    context.user_data["water_checkins"] = water_checkins

    # Update UI to show reset progress
    buttons = [
        [InlineKeyboardButton("✅ I Drank Water", callback_data="water_checkin")],
        [InlineKeyboardButton("📋 View My Schedule", callback_data="water_view_schedule")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    reset_message = (
        f"🔄 <b>Check-ins Reset</b>\n\n"
        f"Your water check-ins for today have been reset to zero.\n\n"
        f"Progress: 0%\n"
        f"{'⬜' * 10}\n\n"
        f"Ready to start tracking your water intake for today!"
    )

    await query.edit_message_text(
        reset_message,
        parse_mode="HTML",
        reply_markup=reply_markup
    )


async def receive_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        height = int(update.message.text)
        if height < 50 or height > 250:
            await update.message.reply_text("⚠️ Please enter a valid height between 50 and 250 cm.")
            return HEIGHT

        # Initialize water_settings
        context.user_data["water_settings"] = {"height": height}
        await update.message.reply_text("⚖️ Now enter your weight in kg (e.g. 65):")
        return WEIGHT
    except ValueError:
        await update.message.reply_text("⚠️ Please enter a valid number for height.")
        return HEIGHT


async def receive_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        weight = int(update.message.text)
        if weight < 20 or weight > 300:
            await update.message.reply_text("⚠️ Please enter a valid weight between 20 and 300 kg.")
            return WEIGHT

        context.user_data["water_settings"]["weight"] = weight

        # Create keyboard for activity level
        activity_buttons = [
            [InlineKeyboardButton("Mostly sitting (office work)", callback_data="water_activity_sedentary")],
            [InlineKeyboardButton("Light activity (walking)", callback_data="water_activity_light")],
            [InlineKeyboardButton("Moderate activity (fast walking)", callback_data="water_activity_moderate")],
            [InlineKeyboardButton("Heavy activity (running)", callback_data="water_activity_heavy")],
            [InlineKeyboardButton("Athlete level (training)", callback_data="water_activity_athlete")]
        ]

        reply_markup = InlineKeyboardMarkup(activity_buttons)
        await update.message.reply_text("🏃‍♂️ What's your typical activity level?", reply_markup=reply_markup)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("⚠️ Please enter a valid number for weight.")
        return WEIGHT


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Return to main menu
    main_menu_keyboard = [
        ["🧮 BMI & Calories", "💧 Water Reminder"],
        ["🍲 Healthy Recipe", "🥦 Food Info"],
        ["💪 Workout Plan", "◀️ Back"]
    ]
    reply_markup = ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)

    await update.message.reply_text("❌ Water reminder setup cancelled.", reply_markup=reply_markup)
    return ConversationHandler.END


async def activity_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Parse data
    _, _, activity = query.data.split("_")

    # Store in water settings
    if "water_settings" not in context.user_data:
        context.user_data["water_settings"] = {}

    context.user_data["water_settings"]["activity"] = activity

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

    # Store in water settings
    if "water_settings" not in context.user_data:
        context.user_data["water_settings"] = {}

    context.user_data["water_settings"]["climate"] = climate

    # Calculate personalized water intake
    settings = context.user_data["water_settings"]
    weight = settings.get("weight", 70)  # Default weight if missing
    activity = settings.get("activity", "moderate")

    # Calculate water intake with optimized formula
    water_intake_ml = calculate_water_intake(weight, activity, climate)
    water_intake_liters = water_intake_ml / 1000

    # Store calculated values
    settings["daily_intake_ml"] = water_intake_ml
    settings["daily_intake_liters"] = water_intake_liters

    # Create message with recommendations
    activity_descriptions = {
        "sedentary": "Mostly sitting (office work)",
        "light": "Light activity (walking)",
        "moderate": "Moderate activity (fast walking)",
        "heavy": "Heavy activity (running)",
        "athlete": "Athlete level (training)"
    }

    # Get height from settings
    height = settings.get("height", 170)  # Default height if missing

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
    message += "Would you like me to set up reminder notifications?"

    # Schedule reminder options
    reminder_buttons = [
        [InlineKeyboardButton("Every 1 hour", callback_data="water_frequency_1")],
        [InlineKeyboardButton("Every 2 hours", callback_data="water_frequency_2")],
        [InlineKeyboardButton("Every 3 hours", callback_data="water_frequency_3")],
        [InlineKeyboardButton("No reminders", callback_data="water_frequency_0")]
    ]
    reply_markup = InlineKeyboardMarkup(reminder_buttons)

    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="HTML")


def calculate_water_intake(weight, activity, climate):
    """Optimized function to calculate water intake based on factors"""
    # Base calculation: 35ml per kg
    water_intake_ml = weight * 35

    # Apply activity factor
    activity_factors = {
        "sedentary": 1.0,
        "light": 1.1,
        "moderate": 1.2,
        "heavy": 1.3,
        "athlete": 1.5
    }
    water_intake_ml *= activity_factors.get(activity, 1.2)  # Default to moderate if invalid

    # Apply climate factor
    climate_factors = {
        "cold": 0.9,
        "temperate": 1.0,
        "hot": 1.2
    }
    water_intake_ml *= climate_factors.get(climate, 1.0)  # Default to temperate if invalid

    return water_intake_ml


async def frequency_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Parse frequency in hours
    hours = int(query.data.split("_")[2])

    # Store in water settings
    context.user_data["water_settings"]["reminder_hours"] = hours

    if hours == 0:
        # User doesn't want reminders
        main_menu_keyboard = [
            ["🧮 BMI & Calories", "💧 Water Reminder"],
            ["🍲 Healthy Recipe", "🥦 Food Info"],
            ["💪 Workout Plan", "◀️ Back"]
        ]

        # Create interactive buttons for water tracking
        buttons = [
            [InlineKeyboardButton("📋 View Schedule", callback_data="water_view_schedule")],
            [InlineKeyboardButton("✅ I Drank Water", callback_data="water_checkin")],
            [InlineKeyboardButton("🗑️ Reset Today's Check-ins", callback_data="water_reset_checkins")]
        ]
        inline_markup = InlineKeyboardMarkup(buttons)

        # Return to main menu with a final message
        await query.edit_message_text(
            "👍 <b>Got it! No reminders needed.</b>\n\n"
            "<i>Pro tip: Many people find it helpful to keep a water bottle visible on their desk "
            "as a passive reminder to stay hydrated.</i>",
            parse_mode="HTML"
        )

        # Send tracking buttons
        await query.message.reply_text(
            "You can track your water intake using these buttons:",
            reply_markup=inline_markup
        )

        # Send main menu
        await query.message.reply_text(
            "What would you like to do next?",
            reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)
        )
        return

    # User wants reminders, ask about time range
    time_buttons = [
        [
            InlineKeyboardButton("8 AM - 6 PM", callback_data="water_time_8_18"),
            InlineKeyboardButton("9 AM - 5 PM", callback_data="water_time_9_17")
        ],
        [
            InlineKeyboardButton("7 AM - 9 PM", callback_data="water_time_7_21"),
            InlineKeyboardButton("10 AM - 8 PM", callback_data="water_time_10_20")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(time_buttons)

    await query.edit_message_text(
        f"⏰ <b>When should I send reminders?</b>\n\n"
        f"I'll remind you every {hours} hour(s) within the time range you select:",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def time_range_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Parse time range
    _, _, start_hour, end_hour = query.data.split("_")
    start_hour = int(start_hour)
    end_hour = int(end_hour)

    # Get user ID explicitly
    user_id = update.effective_user.id

    # Store in water settings
    settings = context.user_data["water_settings"]
    settings["reminder_start_hour"] = start_hour
    settings["reminder_end_hour"] = end_hour

    # Calculate reminders and water distribution
    hours_interval = settings["reminder_hours"]
    active_hours = end_hour - start_hour
    reminders_per_day = max(1, active_hours // hours_interval)
    water_per_reminder = settings["daily_intake_ml"] / reminders_per_day

    # Generate scheduled times
    current_hour = start_hour
    times = []
    while current_hour < end_hour:
        times.append(
            f"• {current_hour}:00 - Drink ~{int(water_per_reminder)}ml ({int(water_per_reminder / 250)} glass)")
        current_hour += hours_interval

    # Store the times for future reference
    settings["schedule_times"] = times
    settings["reminders_active"] = True

    # Generate the schedule message
    schedule_message = f"🔔 <b>Water reminders activated!</b>\n\n"
    schedule_message += f"I'll remind you to drink water every {hours_interval} hour(s) between {start_hour}:00 and {end_hour}:00.\n\n"
    schedule_message += f"<b>Your schedule:</b>\n"
    schedule_message += "\n".join(times)
    schedule_message += "\n\n<i>Staying hydrated helps maintain energy levels and cognitive function!</i>"

    # Check if job queue exists
    has_job_queue = hasattr(context, 'job_queue') and context.job_queue is not None

    if has_job_queue:
        # Clear existing reminders and schedule new ones - pass user_id explicitly
        await clear_water_reminder_jobs(context, user_id)
        await schedule_reminders(update, context, start_hour, end_hour, hours_interval)
    else:
        schedule_message += "\n\n⚠️ <i>Note: Automatic notifications could not be enabled. The schedule is saved but you won't receive automatic reminders.</i>"

    # Edit the current message with schedule details
    await query.edit_message_text(
        schedule_message,
        parse_mode="HTML"
    )

    # Create buttons for water tracking
    buttons = [
        [InlineKeyboardButton("📋 View Schedule", callback_data="water_view_schedule")],
        [InlineKeyboardButton("✅ I Drank Water", callback_data="water_checkin")],
        [InlineKeyboardButton("🗑️ Reset Today's Check-ins", callback_data="water_reset_checkins")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    # Return to main menu
    main_menu_keyboard = [
        ["🧮 BMI & Calories", "💧 Water Reminder"],
        ["🍲 Healthy Recipe", "🥦 Food Info"],
        ["💪 Workout Plan", "◀️ Back"]
    ]

    # Send tracking buttons
    await query.message.reply_text(
        "You can track your water intake using these buttons:",
        reply_markup=reply_markup
    )

    # Send main menu
    await query.message.reply_text(
        "Your water reminders are now set! What would you like to do next?",
        reply_markup=ReplyKeyboardMarkup(main_menu_keyboard, resize_keyboard=True)
    )


async def clear_water_reminder_jobs(context: ContextTypes.DEFAULT_TYPE, user_id=None):
    """Remove all water reminder jobs for the current user"""
    # Safety check
    if not hasattr(context, 'job_queue') or context.job_queue is None:
        print("Warning: Job queue not available")
        return

    # If user_id wasn't passed in, try to get it from context
    if user_id is None:
        # Try different ways to get user_id
        if hasattr(context, '_user_id'):
            user_id = context._user_id
        elif hasattr(context, 'user_id'):
            user_id = context.user_id
        else:
            print("Warning: Could not determine user ID")
            return

    # Get all jobs with this prefix + user_id
    current_jobs = context.job_queue.get_jobs_by_name(f"{JOB_NAME_PREFIX}{user_id}")

    for job in current_jobs:
        job.schedule_removal()


async def schedule_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE, start_hour, end_hour, interval_hours):
    """Schedule actual water reminder jobs"""
    # Safety check
    if not hasattr(context, 'job_queue') or context.job_queue is None:
        print("Warning: Job queue not available, cannot schedule reminders")
        return

    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Calculate water distribution
    settings = context.user_data["water_settings"]
    daily_intake_ml = settings["daily_intake_ml"]
    active_hours = end_hour - start_hour
    reminders_per_day = max(1, active_hours // interval_hours)
    water_per_reminder = daily_intake_ml / reminders_per_day

    # Schedule each reminder
    current_hour = start_hour
    while current_hour < end_hour:
        # Create a time object for this hour
        reminder_time = datetime_time(hour=current_hour, minute=0)

        # Create the reminder message
        reminder_message = (
            f"💧 <b>Water Reminder</b> 💧\n\n"
            f"Time to drink ~{int(water_per_reminder)}ml of water "
            f"({int(water_per_reminder / 250)} glass)!\n\n"
            f"<i>Staying hydrated helps maintain energy and focus.</i>"
        )

        # Schedule the job
        try:
            context.job_queue.run_daily(
                send_water_reminder,
                reminder_time,
                chat_id=chat_id,
                user_id=user_id,
                name=f"{JOB_NAME_PREFIX}{user_id}_{current_hour}",
                data={"message": reminder_message}
            )
            print(f"Scheduled reminder at {reminder_time} for user {user_id}")
        except Exception as e:
            print(f"Error scheduling reminder: {e}")

        current_hour += interval_hours


async def send_water_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Callback function that sends the reminder message"""
    job = context.job
    message = job.data.get("message", "💧 Time to drink some water!")

    # Create interactive buttons for the reminder
    buttons = [
        [InlineKeyboardButton("✅ I Drank Water", callback_data="water_checkin")],
        [InlineKeyboardButton("📋 View My Schedule", callback_data="water_view_schedule")],
        [InlineKeyboardButton("🗑️ Reset Today's Check-ins", callback_data="water_reset_checkins")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    try:
        # Send the message with buttons
        await context.bot.send_message(
            job.chat_id,
            message,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"Error sending reminder: {e}")


async def view_schedule_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the user's water schedule when requested"""
    query = update.callback_query
    await query.answer()

    if "water_settings" not in context.user_data or "daily_intake_liters" not in context.user_data["water_settings"]:
        await query.edit_message_text(
            "⚠️ You don't have a water schedule set up yet. Please use the 'Water Reminder' option from the main menu.",
            parse_mode="HTML"
        )
        return

    # Get stored schedule information
    settings = context.user_data["water_settings"]
    daily_intake_liters = settings["daily_intake_liters"]

    # Check if we have saved schedule times
    if "schedule_times" in settings and settings["schedule_times"]:
        times = settings["schedule_times"]
    else:
        # Calculate schedule if not stored
        start_hour = settings.get("reminder_start_hour", 8)
        end_hour = settings.get("reminder_end_hour", 20)
        hours_interval = settings.get("reminder_hours", 2)

        water_per_reminder = settings["daily_intake_ml"] / max(1, ((end_hour - start_hour) // hours_interval))

        # Generate times
        current_hour = start_hour
        times = []
        while current_hour < end_hour:
            times.append(
                f"• {current_hour}:00 - Drink ~{int(water_per_reminder)}ml ({int(water_per_reminder / 250)} glass)")
            current_hour += hours_interval

    # Create buttons for water tracking
    buttons = [
        [InlineKeyboardButton("✅ I Drank Water", callback_data="water_checkin")],
        [InlineKeyboardButton("🔄 Update Schedule", callback_data="water_new_plan")],
        [InlineKeyboardButton("🗑️ Reset Today's Check-ins", callback_data="water_reset_checkins")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    # Generate schedule message
    schedule_message = (
            f"💧 <b>Your Water Schedule</b>\n\n"
            f"Your recommended daily intake is <b>{daily_intake_liters:.1f} liters</b>.\n\n"
            f"<b>Today's schedule:</b>\n" + "\n".join(times) + "\n\n"
                                                               f"<i>Try to follow this schedule for optimal hydration!</i>"
    )

    await query.edit_message_text(
        schedule_message,
        parse_mode="HTML",
        reply_markup=reply_markup
    )


async def checkin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Record when user drinks water"""
    query = update.callback_query
    await query.answer("Great job staying hydrated! 💧")

    # Get current time
    now = datetime.now()

    # Initialize checkin history if needed
    if "water_checkins" not in context.user_data:
        context.user_data["water_checkins"] = []

    # Add this checkin
    context.user_data["water_checkins"].append({
        "timestamp": now.strftime("%Y-%m-%d %H:%M"),
        "hour": now.hour
    })

    # Filter for today's checkins
    today = now.date()
    today_checkins = [c for c in context.user_data["water_checkins"]
                      if datetime.strptime(c["timestamp"], "%Y-%m-%d %H:%M").date() == today]

    # Get daily target from settings
    daily_intake = "your recommended amount"
    glasses_target = 8  # Default target

    if "water_settings" in context.user_data and "daily_intake_liters" in context.user_data["water_settings"]:
        daily_intake = f"{context.user_data['water_settings']['daily_intake_liters']:.1f} liters"
        glasses_target = int(context.user_data["water_settings"]["daily_intake_liters"] * 4)  # 250ml glasses

    # Calculate progress and create progress bar
    progress_percent = min(100, int((len(today_checkins) / glasses_target) * 100))
    filled = int(10 * progress_percent / 100)  # 10-segment bar
    progress_bar = "🟦" * filled + "⬜" * (10 - filled)

    # Create refreshed buttons
    buttons = [
        [InlineKeyboardButton("✅ I Drank Water", callback_data="water_checkin")],
        [InlineKeyboardButton("📋 View My Schedule", callback_data="water_view_schedule")],
        [InlineKeyboardButton("🗑️ Reset Today's Check-ins", callback_data="water_reset_checkins")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    checkin_message = (
        f"🎉 <b>Water Check-In #{len(today_checkins)}</b>\n\n"
        f"<i>Recorded at: {now.strftime('%H:%M')}</i>\n\n"
        f"<b>Today's progress: {progress_percent}%</b>\n"
        f"{progress_bar}\n\n"
        f"You've had approximately {len(today_checkins) * 250}ml out of {daily_intake} today.\n\n"
        f"{'🎊 Amazing! You reached your goal!' if progress_percent >= 100 else 'Keep it up! Staying hydrated helps with energy, focus, and overall health.'}"
    )

    await query.edit_message_text(
        checkin_message,
        parse_mode="HTML",
        reply_markup=reply_markup
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
    app.add_handler(CallbackQueryHandler(frequency_callback, pattern=r"^water_frequency_"))
    app.add_handler(CallbackQueryHandler(time_range_callback, pattern=r"^water_time_"))
    app.add_handler(CallbackQueryHandler(view_schedule_callback, pattern=r"^water_view_schedule$"))
    app.add_handler(CallbackQueryHandler(checkin_callback, pattern=r"^water_checkin$"))
    app.add_handler(CallbackQueryHandler(new_plan_callback, pattern=r"^water_new_plan$"))
    app.add_handler(CallbackQueryHandler(reset_checkins_callback, pattern=r"^water_reset_checkins$"))