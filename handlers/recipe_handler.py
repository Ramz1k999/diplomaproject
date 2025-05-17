from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters
from services.gemini_service import get_healthy_recipe

INGREDIENTS = 0


async def start_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🍅 Please enter the ingredients you have, separated by commas.\n"
        "Example: chicken, broccoli, garlic"
    )
    return INGREDIENTS


async def receive_ingredients(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    ingredients = [i.strip() for i in text.split(",") if i.strip()]

    if not ingredients:
        await update.message.reply_text("⚠️ Please enter at least one ingredient.")
        return INGREDIENTS

    # Show typing indicator while generating recipe
    await update.message.chat.send_action(action="typing")

    # Get recipe from Gemini
    recipe_markdown = get_healthy_recipe(ingredients)

    # Instead of complex conversion, create a simple HTML-safe version
    lines = recipe_markdown.split('\n')
    html_lines = []

    for line in lines:
        # Handle headings
        if line.startswith('## '):
            html_lines.append(f"<b>{line[3:]}</b>")
        elif line.startswith('### '):
            html_lines.append(f"\n<b>{line[4:]}:</b>")
        # Handle bullet points
        elif line.strip().startswith('• '):
            html_lines.append(line)
        # Handle numbered instructions
        elif line.strip() and line[0].isdigit() and line[1:].startswith('. '):
            html_lines.append(line)
        # Handle bold text
        elif '**' in line:
            # Replace pairs of ** with <b> and </b>
            parts = line.split('**')
            new_line = ''
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Even parts are outside **
                    new_line += part
                else:  # Odd parts are inside **
                    new_line += f"<b>{part}</b>"
            html_lines.append(new_line)
        else:
            html_lines.append(line)

    # Join the HTML lines back together
    recipe_html = '\n'.join(html_lines)

    await update.message.reply_text(
        f"<b>🎉 Here's a recipe using your ingredients!</b>\n\n{recipe_html}",
        parse_mode="HTML"
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Recipe request cancelled.")
    return ConversationHandler.END


recipe_handler = ConversationHandler(
    entry_points=[
        CommandHandler("recipe", start_recipe),
        MessageHandler(filters.Regex("^🍲 Healthy Recipe$"), start_recipe)
    ],
    states={
        INGREDIENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_ingredients)],
    },
    fallbacks=[CommandHandler("cancel;", cancel)],
)