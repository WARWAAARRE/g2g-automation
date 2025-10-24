from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.crud import get_or_create_user
import random
from datetime import datetime, timedelta

router = Router()

def get_orders_keyboard():
    builder = InlineKeyboardBuilder()
    
    builder.add(
        InlineKeyboardButton(text="🔔 НОВЫЕ ЗАКАЗЫ", callback_data="new_orders"),
        InlineKeyboardButton(text="✅ ЗАВЕРШЕННЫЕ", callback_data="completed_orders")
    )
    builder.adjust(1)
    
    builder.row(InlineKeyboardButton(text="🔄 ОБНОВИТЬ", callback_data="refresh_orders"))
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"))
    
    return builder.as_markup()

def generate_mock_orders():
    games = ["Steam", "Valorant", "LoL", "Genshin Impact", "Minecraft"]
    statuses = ["new", "delivered"]
    
    orders = []
    for i in range(random.randint(2, 6)):
        order_time = datetime.now() - timedelta(hours=random.randint(1, 48))
        orders.append({
            'id': f"G2G{random.randint(100000, 999999)}",
            'game': random.choice(games),
            'amount': round(random.uniform(15.99, 89.99), 2),
            'status': random.choice(statuses),
            'time': order_time.strftime('%d.%m.%Y %H:%M'),
            'buyer': f"user{random.randint(1000, 9999)}"
        })
    return orders

@router.message(F.text == "📦 ЗАКАЗЫ G2G")
async def orders_menu(message: Message):
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    mock_orders = generate_mock_orders()
    
    new_orders = [o for o in mock_orders if o['status'] == 'new']
    completed_orders = [o for o in mock_orders if o['status'] == 'delivered']
    
    total_revenue = sum(o['amount'] for o in completed_orders)
    
    menu_text = f"""
📦 УПРАВЛЕНИЕ ЗАКАЗАМИ G2G

📊 Статистика заказов:
• 🔔 Новые: {len(new_orders)}
• ✅ Завершенные: {len(completed_orders)}
• 💰 Общий доход: ${total_revenue}

💡 Автоматическая обработка:
• Автопокупка на LZT при новом заказе
• Автоотправка данных покупателю
• Автоотмена при проблемах
• Проверка заказов каждые 5 минут
"""
    await message.answer(menu_text, reply_markup=get_orders_keyboard())

@router.callback_query(F.data == "new_orders")
async def show_new_orders(callback: CallbackQuery):
    mock_orders = generate_mock_orders()
    new_orders = [o for o in mock_orders if o['status'] == 'new']
    
    if not new_orders:
        await callback.message.answer("🔔 Новых заказов нет")
        await callback.answer()
        return
    
    orders_text = "🔔 НОВЫЕ ЗАКАЗЫ:\n\n"
    
    for order in new_orders:
        orders_text += f"""📦 Заказ #{order['id']}
🎮 Игра: {order['game']}
💳 Сумма: ${order['amount']}
👤 Покупатель: {order['buyer']}
🕐 Создан: {order['time']}
━━━━━━━━━━━━━━━━━━━━
"""
    
    await callback.message.answer(orders_text)
    await callback.answer()

@router.callback_query(F.data == "completed_orders")
async def show_completed_orders(callback: CallbackQuery):
    mock_orders = generate_mock_orders()
    completed_orders = [o for o in mock_orders if o['status'] == 'delivered']
    
    if not completed_orders:
        await callback.message.answer("✅ Завершенных заказов нет")
        await callback.answer()
        return
    
    orders_text = "✅ ЗАВЕРШЕННЫЕ ЗАКАЗЫ:\n\n"
    total_revenue = 0
    
    for order in completed_orders:
        orders_text += f"""✅ Заказ #{order['id']}
🎮 Игра: {order['game']}
💳 Сумма: ${order['amount']}
👤 Покупатель: {order['buyer']}
🕐 Завершен: {order['time']}
━━━━━━━━━━━━━━━━━━━━
"""
        total_revenue += order['amount']
    
    orders_text += f"\n💰 Общий доход: ${total_revenue}"
    
    await callback.message.answer(orders_text)
    await callback.answer()

@router.callback_query(F.data == "refresh_orders")
async def refresh_orders(callback: CallbackQuery):
    await orders_menu(callback.message)
    await callback.answer("📊 Статистика обновлена!")