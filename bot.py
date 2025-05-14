from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram.ext import ApplicationBuilder, PicklePersistence

from handlers.bmi_handler import bmi_handler
from handlers.recipe_handler import recipe_handler
from handlers.food_info_handler import food_info_handler
from handlers.help_handler import help_command, start
from handlers.menu_handler import menu_handler
from handlers.water_handler import register_water_handlers
from handlers.workout_handler import workout_handler

import config
from handlers.workout_handler import workout_handler


def main():
    persistence = PicklePersistence(filepath="bot_data.pickle")

    # Build application with job queue enabled and persistence
    app = (ApplicationBuilder()
           .token(config.BOT_TOKEN)
           .persistence(persistence)
           .build())

    app.add_handler(CommandHandler("start", start))

    # Register handlers
    app.add_handler(help_command)
    app.add_handler(bmi_handler)
    app.add_handler(recipe_handler)
    app.add_handler(food_info_handler)
    register_water_handlers(app)
    app.add_handler(workout_handler)
    app.add_handler(menu_handler)




    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
