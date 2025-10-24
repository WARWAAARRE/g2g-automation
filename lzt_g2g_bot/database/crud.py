# database/crud.py
import aiosqlite
import json
from datetime import datetime, timedelta

# ===== USER METHODS =====
async def get_or_create_user(telegram_id: int, username: str = None, 
                           first_name: str = None, last_name: str = None):
    """Получает или создает пользователя"""
    async with aiosqlite.connect('database.db') as db:
        # Проверяем существующего пользователя
        cursor = await db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        )
        user = await cursor.fetchone()
        
        if not user:
            # Создаем нового пользователя
            subscription_expiry = (datetime.now() + timedelta(days=30)).isoformat()
            
            await db.execute(
                '''INSERT INTO users 
                (telegram_id, username, first_name, last_name, subscription_expiry) 
                VALUES (?, ?, ?, ?, ?)''',
                (telegram_id, username, first_name, last_name, subscription_expiry)
            )
            await db.commit()
            
            # Получаем созданного пользователя
            cursor = await db.execute(
                "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
            )
            user = await cursor.fetchone()
            
            # Создаем настройки по умолчанию
            await db.execute(
                '''INSERT INTO user_settings (user_id) VALUES (?)''',
                (user[0],)  # user[0] - это id пользователя
            )
            await db.commit()
        
        return user

async def update_subscription(telegram_id: int, subscription_type: str):
    """Обновляет тариф пользователя"""
    async with aiosqlite.connect('database.db') as db:
        subscription_expiry = (datetime.now() + timedelta(days=30)).isoformat()
        await db.execute(
            "UPDATE users SET subscription_type = ?, subscription_expiry = ? WHERE telegram_id = ?",
            (subscription_type, subscription_expiry, telegram_id)
        )
        await db.commit()

async def get_active_users():
    """Получает всех активных пользователей"""
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.execute(
            "SELECT * FROM users WHERE is_active = TRUE"
        )
        return await cursor.fetchall()

# ===== API KEYS METHODS =====
async def get_user_api_keys(user_id: int):
    """Получает API ключи пользователя"""
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.execute(
            "SELECT * FROM user_api_keys WHERE user_id = ?", (user_id,)
        )
        return await cursor.fetchone()

async def save_lzt_token(user_id: int, token: str):
    """Сохраняет LZT токен"""
    async with aiosqlite.connect('database.db') as db:
        # Проверяем существующие ключи
        cursor = await db.execute(
            "SELECT id FROM user_api_keys WHERE user_id = ?", (user_id,)
        )
        existing = await cursor.fetchone()
        
        if existing:
            # Обновляем существующие
            await db.execute(
                "UPDATE user_api_keys SET lzt_token = ?, last_checked = ? WHERE user_id = ?",
                (token, datetime.now().isoformat(), user_id)
            )
        else:
            # Создаем новые
            await db.execute(
                '''INSERT INTO user_api_keys 
                (user_id, lzt_token, last_checked) 
                VALUES (?, ?, ?)''',
                (user_id, token, datetime.now().isoformat())
            )
        
        await db.commit()

async def save_g2g_keys(user_id: int, api_key: str, secret: str, g2g_user_id: str):
    """Сохраняет G2G ключи"""
    async with aiosqlite.connect('database.db') as db:
        # Проверяем существующие ключи
        cursor = await db.execute(
            "SELECT id FROM user_api_keys WHERE user_id = ?", (user_id,)
        )
        existing = await cursor.fetchone()
        
        if existing:
            # Обновляем существующие
            await db.execute(
                """UPDATE user_api_keys 
                SET g2g_api_key = ?, g2g_secret = ?, g2g_user_id = ?, last_checked = ? 
                WHERE user_id = ?""",
                (api_key, secret, g2g_user_id, datetime.now().isoformat(), user_id)
            )
        else:
            # Создаем новые
            await db.execute(
                '''INSERT INTO user_api_keys 
                (user_id, g2g_api_key, g2g_secret, g2g_user_id, last_checked) 
                VALUES (?, ?, ?, ?, ?)''',
                (user_id, api_key, secret, g2g_user_id, datetime.now().isoformat())
            )
        
        await db.commit()

# ===== SETTINGS METHODS =====
async def get_user_settings(user_id: int):
    """Получает настройки пользователя"""
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.execute(
            "SELECT * FROM user_settings WHERE user_id = ?", (user_id,)
        )
        return await cursor.fetchone()

async def update_user_settings(user_id: int, updates: dict):
    """Обновляет настройки пользователя"""
    async with aiosqlite.connect('database.db') as db:
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values())
        values.append(user_id)
        
        await db.execute(
            f"UPDATE user_settings SET {set_clause}, updated_at = ? WHERE user_id = ?",
            values + [datetime.now().isoformat()]
        )
        await db.commit()

# ===== OFFERS METHODS =====
async def create_user_offer(user_id: int, lzt_item_id: str, g2g_offer_id: str, title: str, price: float, category: str):
    """Создает запись об оффере"""
    async with aiosqlite.connect('database.db') as db:
        await db.execute(
            '''INSERT INTO user_offers 
            (user_id, lzt_item_id, g2g_offer_id, title, price, category) 
            VALUES (?, ?, ?, ?, ?, ?)''',
            (user_id, lzt_item_id, g2g_offer_id, title, price, category)
        )
        await db.commit()

async def get_user_active_offers(user_id: int):
    """Получает активные офферы пользователя"""
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.execute(
            "SELECT * FROM user_offers WHERE user_id = ? AND status = 'active'",
            (user_id,)
        )
        return await cursor.fetchall()

async def get_offer_by_g2g_id(g2g_offer_id: str):
    """Находит оффер по G2G ID"""
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.execute(
            "SELECT * FROM user_offers WHERE g2g_offer_id = ?",
            (g2g_offer_id,)
        )
        return await cursor.fetchone()

async def update_offer_status(offer_id: int, status: str):
    """Обновляет статус оффера"""
    async with aiosqlite.connect('database.db') as db:
        await db.execute(
            "UPDATE user_offers SET status = ?, updated_at = ? WHERE id = ?",
            (status, datetime.now().isoformat(), offer_id)
        )
        await db.commit()

# ===== ORDERS METHODS =====
async def create_order(user_id: int, offer_id: int, g2g_order_id: str, status: str = 'new'):
    """Создает запись о заказе"""
    async with aiosqlite.connect('database.db') as db:
        await db.execute(
            '''INSERT INTO user_orders 
            (user_id, offer_id, g2g_order_id, status) 
            VALUES (?, ?, ?, ?)''',
            (user_id, offer_id, g2g_order_id, status)
        )
        await db.commit()

async def get_user_orders(user_id: int, status: str = None):
    """Получает заказы пользователя"""
    async with aiosqlite.connect('database.db') as db:
        if status:
            cursor = await db.execute(
                "SELECT * FROM user_orders WHERE user_id = ? AND status = ?",
                (user_id, status)
            )
        else:
            cursor = await db.execute(
                "SELECT * FROM user_orders WHERE user_id = ?",
                (user_id,)
            )
        return await cursor.fetchall()

async def update_order_status(order_id: int, status: str):
    """Обновляет статус заказа"""
    async with aiosqlite.connect('database.db') as db:
        await db.execute(
            "UPDATE user_orders SET status = ?, updated_at = ? WHERE id = ?",
            (status, datetime.now().isoformat(), order_id)
        )
        await db.commit()

# ===== STATISTICS METHODS =====
async def get_user_offers_stats(user_id: int):
    """Статистика офферов пользователя"""
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.execute(
            "SELECT * FROM user_offers WHERE user_id = ?",
            (user_id,)
        )
        offers = await cursor.fetchall()
        
        active = len([o for o in offers if o[8] == 'active'])  # status field
        sold = len([o for o in offers if o[8] == 'sold'])
        
        return {
            'total': len(offers),
            'active': active,
            'sold': sold,
            'limit': 20  # Будет зависеть от тарифа
        }

async def get_user_orders_stats(user_id: int):
    """Статистика заказов пользователя"""
    async with aiosqlite.connect('database.db') as db:
        cursor = await db.execute(
            "SELECT * FROM user_orders WHERE user_id = ?",
            (user_id,)
        )
        orders = await cursor.fetchall()
        
        return {
            'new': len([o for o in orders if o[4] == 'new']),
            'processing': len([o for o in orders if o[4] == 'processing']),
            'delivered': len([o for o in orders if o[4] == 'delivered']),
            'cancelled': len([o for o in orders if o[4] == 'cancelled'])
        }