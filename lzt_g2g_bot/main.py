import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import config
from database import init_db
from handlers.start import router as start_router
from handlers.api_setup import router as api_router
from handlers.subscriptions import router as subscriptions_router
from handlers.parser import router as parser_router
from handlers.auto_posting import router as auto_posting_router
from handlers.orders import router as orders_router
from services.order_checker import check_pending_orders

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Главная функция бота"""
    try:
        # Инициализация базы данных
        await init_db()
        logger.info("✅ Database initialized")
        
        # Создание бота и диспетчера
        bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        dp = Dispatcher()
        
        # Регистрация ВСЕХ роутеров
        dp.include_router(start_router)
        dp.include_router(api_router)
        dp.include_router(subscriptions_router)
        dp.include_router(parser_router)
        dp.include_router(auto_posting_router)
        dp.include_router(orders_router)
        
        # Запускаем планировщик для проверки заказов каждые 5 минут
        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            check_pending_orders,
            'interval',
            minutes=5,  # 🔄 Каждые 5 минут!
            args=[bot]
        )
        scheduler.start()
        logger.info("✅ Order checker scheduler started (every 5 minutes)")
        
        # Запуск бота
        logger.info("✅ Bot starting...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())