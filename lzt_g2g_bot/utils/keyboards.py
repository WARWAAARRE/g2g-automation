from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔑 НАСТРОИТЬ API КЛЮЧИ")],
            [KeyboardButton(text="💳 ВЫБРАТЬ ТАРИФ")],
            [KeyboardButton(text="🎯 НАСТРОИТЬ ПАРСЕР")],
            [KeyboardButton(text="🔄 АВТОСИНХРОНИЗАЦИЯ"), KeyboardButton(text="📦 ЗАКАЗЫ G2G")],
            [KeyboardButton(text="❓ ПОМОЩЬ И ИНСТРУКЦИИ")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )
    return keyboard

def get_api_setup_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔑 LZT API", callback_data="setup_lzt")],
            [InlineKeyboardButton(text="🔑 G2G API", callback_data="setup_g2g")],
            [InlineKeyboardButton(text="🔄 Проверить все", callback_data="check_all_apis")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")]
        ]
    )
    return keyboard

def get_back_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="api_setup")]
        ]
    )
    return keyboard