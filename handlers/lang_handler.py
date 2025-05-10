from aiogram import types, Dispatcher

# Store user language preference in-memory
user_lang = {}

# Translation strings
texts = {
    "start": {
        "en": (
            "👋 *Welcome to the Health Support Bot!*\n\n"
            "I can help you with:\n\n"
            "⚖️ `/bmi` – Calculate your BMI and get daily calorie advice\n"
            "💧 `/water` – See how much water you need to drink\n"
            "🍳 `/recipe` – Get healthy recipes from your ingredients\n"
            "🥗 `/info` – Find nutrition info for any food\n\n"
            "🌐 Use `/language` to switch the bot language."
        ),
        "ru": (
            "👋 *Добро пожаловать в бот здоровья!*\n\n"
            "Я могу помочь вам:\n\n"
            "⚖️ `/bmi` – Рассчитать ИМТ и дневную норму калорий\n"
            "💧 `/water` – Узнать, сколько воды нужно пить\n"
            "🍳 `/recipe` – Рецепты здоровой еды из ваших продуктов\n"
            "🥗 `/info` – Информация о составе любого продукта\n\n"
            "🌐 Используйте `/language`, чтобы сменить язык."
        ),
        "uz": (
            "👋 *Salomatlik botiga xush kelibsiz!*\n\n"
            "Men sizga yordam bera olaman:\n\n"
            "⚖️ `/bmi` – BMI hisoblash va kaloriya tavsiyasi\n"
            "💧 `/water` – Necha litr suv ichish kerakligini bilish\n"
            "🍳 `/recipe` – Mavjud mahsulotlardan sog‘lom retseptlar\n"
            "🥗 `/info` – Mahsulotlar haqida oziqlanish ma'lumoti\n\n"
            "🌐 Tilni almashtirish uchun `/language` buyrug'idan foydalaning."
        ),
    },
    "language_prompt": "🌐 Choose your language:",
    "language_set": {
        "en": "✅ Language set to English.",
        "ru": "✅ Язык установлен на Русский.",
        "uz": "✅ Til O‘zbek tiliga o‘zgartirildi.",
    }
}

async def choose_lang(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇺🇿 O‘zbek", callback_data="lang_uz"),
    )
    await message.answer(texts["language_prompt"], reply_markup=keyboard)

async def set_lang(callback_query: types.CallbackQuery):
    lang = callback_query.data.split('_')[1]
    user_lang[callback_query.from_user.id] = lang
    await callback_query.message.answer(texts["language_set"][lang])
    await callback_query.answer()

def get_user_lang(user_id):
    return user_lang.get(user_id, 'en')  # Default to English

def get_text(user_id, key):
    lang = get_user_lang(user_id)
    return texts[key][lang]

def register(dp: Dispatcher):
    dp.register_message_handler(choose_lang, commands=['language'])
    dp.register_callback_query_handler(set_lang, lambda c: c.data.startswith('lang_'))
