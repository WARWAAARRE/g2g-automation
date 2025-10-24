from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.crud import get_or_create_user, get_user_settings, update_user_settings
import asyncio

router = Router()

LZT_CATEGORIES = {
    "steam": "Steam",
    "valorant": "Valorant", 
    "lol": "LoL",
    "genshin-impact": "Genshin Impact",
    "honkai-star-rail": "Honkai: Star Rail",
    "zenless-zone-zero": "Zenless Zone Zero", 
    "minecraft": "Minecraft",
    "brawl-stars": "Brawl Stars",
    "clash-of-clans": "Clash of Clans"
}

class ParserStates(StatesGroup):
    waiting_markup = State()
    waiting_price_min = State()
    waiting_price_max = State()
    waiting_activity_filter = State()
    waiting_age_filter = State()

def get_parser_keyboard(selected_categories: list = None):
    if selected_categories is None:
        selected_categories = []
    
    builder = InlineKeyboardBuilder()
    
    for category_id, category_name in LZT_CATEGORIES.items():
        emoji = "✅" if category_id in selected_categories else "⚪"
        builder.add(InlineKeyboardButton(
            text=f"{emoji} {category_name}", 
            callback_data=f"cat_{category_id}"
        ))
    
    builder.adjust(2)
    
    builder.row(
        InlineKeyboardButton(text="💰 Наценка", callback_data="set_markup"),
        InlineKeyboardButton(text="📊 Ценовой диапазон", callback_data="set_price_range")
    )
    
    builder.row(
        InlineKeyboardButton(text="🕐 Фильтр отлежки", callback_data="set_activity_filter"),
        InlineKeyboardButton(text="📅 Фильтр давности", callback_data="set_age_filter")  
    )
    
    builder.row(InlineKeyboardButton(text="🚀 ЗАПУСТИТЬ ПАРСИНГ", callback_data="start_parsing"))
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"))
    
    return builder.as_markup()

@router.message(F.text == "🎯 НАСТРОИТЬ ПАРСЕР")
async def parser_menu(message: Message):
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    settings = await get_user_settings(user[0])
    
    selected_cats = []
    if settings and settings[3]:  # parser_categories
        try:
            selected_cats = eval(settings[3])
        except:
            selected_cats = []
    
    markup = settings[2] if settings else 20
    price_min = settings[5] if settings else 1
    price_max = settings[6] if settings else 100
    activity = settings[8] if settings else '7'
    age = settings[7] if settings else 'any'
    
    menu_text = f"""
🎯 НАСТРОЙКА ПАРСЕРА LZT

📊 Текущие настройки:
• Наценка: {markup}%
• Мин. цена: ${price_min}
• Макс. цена: ${price_max}
• Отлежка: {activity}+ дней
• Давность: {age}

🎮 Выберите категории для парсинга:
"""
    await message.answer(menu_text, reply_markup=get_parser_keyboard(selected_cats))

@router.callback_query(F.data.startswith("cat_"))
async def toggle_category(callback: CallbackQuery):
    category_id = callback.data.replace("cat_", "")
    
    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name
    )
    
    settings = await get_user_settings(user[0])
    
    current_cats = []
    if settings and settings[3]:
        try:
            current_cats = eval(settings[3])
        except:
            current_cats = []
    
    if category_id in current_cats:
        current_cats.remove(category_id)
    else:
        current_cats.append(category_id)
    
    await update_user_settings(user[0], {"parser_categories": str(current_cats)})
    
    await callback.message.edit_reply_markup(reply_markup=get_parser_keyboard(current_cats))
    await callback.answer()

@router.callback_query(F.data == "set_markup")
async def set_markup_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("💯 Введите процент наценки (например: 20):")
    await state.set_state(ParserStates.waiting_markup)
    await callback.answer()

@router.message(ParserStates.waiting_markup)
async def process_markup(message: Message, state: FSMContext):
    try:
        markup = int(message.text.strip())
        if markup < 1 or markup > 500:
            await message.answer("❌ Наценка должна быть от 1% до 500%. Попробуйте еще раз:")
            return
        
        user = await get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        await update_user_settings(user[0], {"markup_percent": markup})
        
        await message.answer(f"✅ Наценка установлена: {markup}%")
        await parser_menu(message)
        
    except ValueError:
        await message.answer("❌ Введите число. Попробуйте еще раз:")
        return
    
    await state.clear()

@router.callback_query(F.data == "set_price_range")
async def set_price_range_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("💰 Введите минимальную цену в $ (например: 5):")
    await state.set_state(ParserStates.waiting_price_min)
    await callback.answer()

@router.message(ParserStates.waiting_price_min)
async def process_price_min(message: Message, state: FSMContext):
    try:
        price_min = int(message.text.strip())
        if price_min < 1:
            await message.answer("❌ Цена должна быть больше 0. Попробуйте еще раз:")
            return
        
        await state.update_data(price_min=price_min)
        await message.answer("💰 Теперь введите максимальную цену в $ (например: 100):")
        await state.set_state(ParserStates.waiting_price_max)
        
    except ValueError:
        await message.answer("❌ Введите число. Попробуйте еще раз:")
        return

@router.message(ParserStates.waiting_price_max)
async def process_price_max(message: Message, state: FSMContext):
    try:
        price_max = int(message.text.strip())
        data = await state.get_data()
        price_min = data.get('price_min', 1)
        
        if price_max <= price_min:
            await message.answer("❌ Максимальная цена должна быть больше минимальной. Попробуйте еще раз:")
            return
        
        user = await get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        await update_user_settings(user[0], {
            "price_min": price_min,
            "price_max": price_max
        })
        
        await message.answer(f"✅ Ценовой диапазон установлен: ${price_min} - ${price_max}")
        await parser_menu(message)
        
    except ValueError:
        await message.answer("❌ Введите число. Попробуйте еще раз:")
        return
    
    await state.clear()

@router.callback_query(F.data == "start_parsing")
async def start_parsing(callback: CallbackQuery):
    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name, 
        last_name=callback.from_user.last_name
    )
    
    settings = await get_user_settings(user[0])
    
    if not settings or not settings[3] or settings[3] == "[]":
        await callback.answer("❌ Сначала выберите категории для парсинга!")
        return
    
    await callback.message.answer("🔍 Запускаю парсинг аккаунтов с LZT...")
    
    # Имитация парсинга
    await asyncio.sleep(2)
    
    found_count = 8  # Заглушка
    categories = eval(settings[3]) if settings and settings[3] else []
    
    result_text = f"""
📊 РЕЗУЛЬТАТЫ ПАРСИНГА

✅ Найдено аккаунтов: {found_count}
🎯 Категории: {', '.join([LZT_CATEGORIES.get(cat, cat) for cat in categories[:3]])}
💰 Диапазон цен: ${settings[5] if settings else 1} - ${settings[6] if settings else 100}
⏰ Время выполнения: 2.8 сек

💡 Найденные аккаунты будут автоматически размещены на G2G с наценкой {settings[2] if settings else 20}%
"""
    await callback.message.answer(result_text)
    await callback.answer("Парсинг завершен!")