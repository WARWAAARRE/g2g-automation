# services/order_checker.py
import logging
from database.crud import get_active_users, get_user_api_keys, get_user_orders_stats
from services.encryption import encryption_service

logger = logging.getLogger(__name__)

async def check_pending_orders(bot):
    """Проверяет новые заказы каждые 5 минут"""
    logger.info("🔍 Checking for new orders...")
    
    try:
        users = await get_active_users()
        
        for user in users:
            try:
                await process_user_orders(user, bot)
            except Exception as e:
                logger.error(f"Error processing orders for user {user[0]}: {e}")
                
    except Exception as e:
        logger.error(f"Error in order checker: {e}")

async def process_user_orders(user, bot):
    """Обрабатывает заказы конкретного пользователя"""
    # Получаем API ключи пользователя
    api_keys = await get_user_api_keys(user[0])
    if not api_keys or not api_keys[3]:  # g2g_api_key
        return
    
    # Здесь будет реальная проверка заказов с G2G API
    # Сейчас имитируем проверку
    orders_stats = await get_user_orders_stats(user[0])
    new_orders_count = orders_stats.get('new', 0)
    
    if new_orders_count > 0:
        # Отправляем уведомление пользователю
        try:
            await bot.send_message(
                user[1],  # telegram_id
                f"🔔 У вас {new_orders_count} новых заказов!\n"
                f"Перейдите в раздел '📦 ЗАКАЗЫ G2G' для просмотра."
            )
            logger.info(f"Notified user {user[1]} about {new_orders_count} new orders")
        except Exception as e:
            logger.error(f"Failed to send notification to user {user[1]}: {e}")

async def get_mock_orders():
    """Заглушка для теста - возвращает тестовые заказы"""
    # В реальной версии здесь будет запрос к G2G API
    return []