from telegram.ext import ApplicationBuilder, CommandHandler

from handlers.bmi_handler import bmi_handler
from handlers.recipe_handler import recipe_handler
from handlers.food_info_handler import food_info_handler
from handlers.help_handler import help_command, start
from handlers.menu_handler import menu_handler
from handlers.water_handler import water_handler, register_water_handlers

import config


def main():
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # Register handlers
    app.add_handler(help_command)
    app.add_handler(bmi_handler)
    app.add_handler(recipe_handler)
    app.add_handler(food_info_handler)
    register_water_handlers(app)
    app.add_handler(menu_handler)




    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
