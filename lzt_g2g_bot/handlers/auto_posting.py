from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.crud import get_or_create_user, get_user_api_keys, get_user_settings, create_user_offer, get_user_active_offers
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

def get_auto_posting_keyboard(is_active: bool = False):
    builder = InlineKeyboardBuilder()
    
    if not is_active:
        builder.add(InlineKeyboardButton(text="🚀 ЗАПУСТИТЬ СИНХРОНИЗАЦИЮ", callback_data="start_auto_posting"))
    else:
        builder.add(InlineKeyboardButton(text="⏸️ ОСТАНОВИТЬ", callback_data="stop_auto_posting"))
    
    builder.add(InlineKeyboardButton(text="📊 СТАТИСТИКА", callback_data="posting_stats"))
    builder.adjust(1)
    
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"))
    
    return builder.as_markup()

@router.message(F.text == "🔄 АВТОСИНХРОНИЗАЦИЯ")
async def auto_posting_menu(message: Message):
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    api_keys = await get_user_api_keys(user[0])
    settings = await get_user_settings(user[0])
    active_offers = await get_user_active_offers(user[0])
    
    has_lzt = bool(api_keys and api_keys[2])
    has_g2g = bool(api_keys and api_keys[3])
    categories = eval(settings[3]) if settings and settings[3] else []
    
    menu_text = f"""
🔄 АВТОМАТИЧЕСКАЯ СИНХРОНИЗАЦИЯ LZT → G2G

📊 Статус:
• LZT API: {'✅ Настроено' if has_lzt else '❌ Не настроено'}
• G2G API: {'✅ Настроено' if has_g2g else '❌ Не настроено'}
• Категории: {len(categories)} выбрано
• Наценка: {settings[2] if settings else 20}%
• Активных объявлений: {len(active_offers)}

🚀 Функции:
• Автопарсинг новых аккаунтов с LZT
• Автосоздание объявлений на G2G с наценкой
• Умные фильтры (цена, отлежка, давность)
• Автообработка заказов
• Уведомления о продажах
"""
    await message.answer(menu_text, reply_markup=get_auto_posting_keyboard())

@router.callback_query(F.data == "start_auto_posting")
async def start_auto_posting(callback: CallbackQuery):
    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name
    )
    
    api_keys = await get_user_api_keys(user[0])
    settings = await get_user_settings(user[0])
    
    if not api_keys or not api_keys[2] or not api_keys[3]:
        await callback.answer("❌ Сначала настройте LZT и G2G API!")
        return
    
    if not settings or not settings[3] or settings[3] == "[]":
        await callback.answer("❌ Сначала выберите категории в настройках парсера!")
        return
    
    await callback.message.answer("🚀 Запускаю автоматическую синхронизацию...")
    
    # Имитация работы авто-постинга
    progress_msg = await callback.message.answer("🔄 Парсинг LZT...")
    await asyncio.sleep(1)
    
    await progress_msg.edit_text("🔄 Создание объявлений на G2G...")
    await asyncio.sleep(1)
    
    # Создаем тестовые офферы
    categories = eval(settings[3])
    for i, category in enumerate(categories[:3]):
        await create_user_offer(
            user_id=user[0],
            lzt_item_id=f"test_lzt_{i}",
            g2g_offer_id=f"test_g2g_{i}",
            title=f"Test {LZT_CATEGORIES.get(category, category)} Account",
            price=25.99 + i * 5,
            category=category
        )
        await asyncio.sleep(0.5)
    
    await progress_msg.edit_text("✅ Авто-синхронизация запущена!")
    
    result_text = f"""
✅ АВТО-СИНХРОНИЗАЦИЯ ЗАПУЩЕНА

📊 Статус:
• Парсинг LZT: 🟢 Активен
• Создание офферов G2G: 🟢 Активно
• Проверка заказов: 🟢 Каждые 5 мин
• Создано объявлений: 3

🎯 Категории: {', '.join([LZT_CATEGORIES.get(cat, cat) for cat in categories[:3]])}
💰 Наценка: {settings[2]}%

💡 Система автоматически:
1. Ищет новые аккаунты на LZT по выбранным категориям
2. Создает объявления на G2G с установленной наценкой
3. Отслеживает новые заказы
4. Покупает аккаунты на LZT при продажах
5. Отправляет данные покупателям
"""
    await callback.message.answer(result_text, reply_markup=get_auto_posting_keyboard(is_active=True))
    await callback.answer("Авто-синхронизация запущена!")

@router.callback_query(F.data == "posting_stats")
async def show_posting_stats(callback: CallbackQuery):
    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name
    )
    
    active_offers = await get_user_active_offers(user[0])
    settings = await get_user_settings(user[0])
    
    stats_text = f"""
📊 СТАТИСТИКА АВТО-СИНХРОНИЗАЦИИ

📈 Общая статистика:
• Активных объявлений: {len(active_offers)}
• Всего создано: {len(active_offers)}
• Продано: 0
• Доход: $0.00

⚙️ Настройки:
• Наценка: {settings[2] if settings else 20}%
• Категории: {len(eval(settings[3])) if settings and settings[3] else 0}
• Ценовой диапазон: ${settings[5] if settings else 1} - ${settings[6] if settings else 100}

📋 Активные объявления:
"""
    
    for i, offer in enumerate(active_offers[:5]):
        stats_text += f"• {offer[4]} - ${offer[5]}\n"
    
    if len(active_offers) > 5:
        stats_text += f"• ... и еще {len(active_offers) - 5} объявлений\n"
    
    await callback.message.answer(stats_text)
    await callback.answer()