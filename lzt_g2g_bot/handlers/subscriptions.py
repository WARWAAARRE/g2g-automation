from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.crud import get_or_create_user, update_subscription
from datetime import datetime, timedelta

router = Router()

SUBSCRIPTION_PLANS = {
    "basic": {
        "name": "🟢 БАЗОВЫЙ",
        "price": 4,
        "daily_limit": 20,
        "features": [
            "20 аккаунтов в сутки",
            "Автопарсинг LZT", 
            "Автовыставление G2G",
            "Уведомления о заказах"
        ]
    },
    "premium": {
        "name": "🟡 ПРЕМИУМ", 
        "price": 12,
        "daily_limit": 50,
        "features": [
            "50 аккаунтов в сутки",
            "Приоритетная поддержка",
            "Расширенная статистика", 
            "Все функции Базового"
        ]
    },
    "pro": {
        "name": "🔴 PRO",
        "price": 20, 
        "daily_limit": 100,
        "features": [
            "100 аккаунтов в сутки",
            "Кастомные настройки",
            "API доступ",
            "Все функции Премиум"
        ]
    }
}

def get_subscription_keyboard():
    builder = InlineKeyboardBuilder()
    
    builder.add(
        InlineKeyboardButton(text="🟢 БАЗОВЫЙ - $4", callback_data="sub_basic"),
        InlineKeyboardButton(text="🟡 ПРЕМИУМ - $12", callback_data="sub_premium"),
        InlineKeyboardButton(text="🔴 PRO - $20", callback_data="sub_pro")
    )
    builder.adjust(1)
    
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"))
    
    return builder.as_markup()

@router.message(F.text == "💳 ВЫБРАТЬ ТАРИФ")
async def subscription_menu(message: Message):
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name, 
        last_name=message.from_user.last_name
    )
    
    current_plan = SUBSCRIPTION_PLANS.get(user[6], {}).get('name', 'Базовый') if user else 'Базовый'
    
    menu_text = f"""
💳 ВЫБОР ТАРИФА

Ваш текущий тариф: {current_plan}

🟢 БАЗОВЫЙ - $4/мес
├─ 20 аккаунтов в сутки
├─ Автопарсинг LZT
├─ Автовыставление G2G
└─ Уведомления о заказах

🟡 ПРЕМИУМ - $12/мес  
├─ 50 аккаунтов в сутки
├─ Приоритетная поддержка
├─ Расширенная статистика
└─ Все функции Базового

🔴 PRO - $20/мес
├─ 100 аккаунтов в сутки
├─ Кастомные настройки  
├─ API доступ
└─ Все функции Премиум

Выберите тариф:
"""
    await message.answer(menu_text, reply_markup=get_subscription_keyboard())

@router.callback_query(F.data.startswith("sub_"))
async def select_subscription(callback: CallbackQuery):
    plan_type = callback.data.replace("sub_", "")
    plan = SUBSCRIPTION_PLANS.get(plan_type)
    
    if not plan:
        await callback.answer("❌ Тариф не найден")
        return
    
    await update_subscription(callback.from_user.id, plan_type)
    
    expiry_date = (datetime.now() + timedelta(days=30)).strftime('%d.%m.%Y')
    
    success_text = f"""
✅ ТАРИФ АКТИВИРОВАН!

{plan['name']} - ${plan['price']}/мес

📊 Лимиты:
• {plan['daily_limit']} аккаунтов в сутки

💡 Особенности:
{chr(10).join(['• ' + feature for feature in plan['features']])}

Тариф активен до: {expiry_date}
"""
    await callback.message.edit_text(success_text)
    await callback.answer(f"Тариф {plan['name']} активирован!")