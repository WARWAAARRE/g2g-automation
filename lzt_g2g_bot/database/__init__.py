# database/__init__.py
import aiosqlite
import logging

logger = logging.getLogger(__name__)

async def init_db():
    """Инициализация базы данных"""
    try:
        async with aiosqlite.connect('database.db') as db:
            # Таблица пользователей
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    subscription_type TEXT DEFAULT 'basic',
                    subscription_expiry TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Таблица API ключей
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    lzt_token TEXT,
                    g2g_api_key TEXT,
                    g2g_secret TEXT,
                    g2g_user_id TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    last_checked TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Таблица настроек
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    markup_percent INTEGER DEFAULT 20,
                    markup_fixed INTEGER DEFAULT 0,
                    parser_categories TEXT DEFAULT '[]',
                    price_min INTEGER DEFAULT 1,
                    price_max INTEGER DEFAULT 100,
                    account_age_filter TEXT DEFAULT 'any',
                    last_activity_filter TEXT DEFAULT '7',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Таблица офферов
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_offers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    lzt_item_id TEXT,
                    g2g_offer_id TEXT,
                    title TEXT,
                    price REAL,
                    markup_percent INTEGER DEFAULT 20,
                    category TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Таблица заказов
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    offer_id INTEGER,
                    g2g_order_id TEXT,
                    status TEXT DEFAULT 'new',
                    amount REAL,
                    lzt_purchase_data TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (offer_id) REFERENCES user_offers (id)
                )
            ''')
            
            await db.commit()
            logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        raise

async def get_db():
    """Получаем соединение с БД"""
    return await aiosqlite.connect('database.db')