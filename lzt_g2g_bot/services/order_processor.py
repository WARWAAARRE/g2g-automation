import asyncio
from typing import Dict, Optional
from services.lzt_api import purchase_account
from services.g2g_api import deliver_order, cancel_order
from services.encryption import encryption_service
from database.crud import get_user_api_keys, get_offer_by_g2g_id, update_offer_status, create_order

class OrderProcessor:
    def __init__(self, db, user_id: int):
        self.db = db
        self.user_id = user_id
    
    async def process_new_order(self, g2g_order_data: Dict) -> Dict:
        """Обрабатывает новый заказ с G2G"""
        # Получаем информацию об оффере
        offer = await get_offer_by_g2g_id(self.db, g2g_order_data['offer_id'])
        if not offer:
            return {'error': 'Offer not found'}
        
        # Получаем API ключи
        api_keys = await get_user_api_keys(self.db, self.user_id)
        if not api_keys:
            return {'error': 'API keys not found'}
        
        # Дешифруем ключи
        lzt_token = encryption_service.decrypt(api_keys.lzt_token)
        g2g_api_key = encryption_service.decrypt(api_keys.g2g_api_key)
        g2g_secret = encryption_service.decrypt(api_keys.g2g_secret)
        g2g_user_id = api_keys.g2g_user_id
        
        try:
            # Покупаем аккаунт на LZT
            lzt_purchase = await purchase_account(
                offer.lzt_item_id, 
                offer.price / (1 + offer.markup_percent / 100),  # Оригинальная цена
                lzt_token
            )
            
            if lzt_purchase and lzt_purchase.get('success'):
                # Отправляем данные покупателю на G2G
                delivery_result = await deliver_order(
                    g2g_api_key, g2g_secret, g2g_user_id,
                    g2g_order_data['order_id'],
                    lzt_purchase['account_data']
                )
                
                if delivery_result:
                    # Обновляем статусы
                    await update_offer_status(self.db, offer.id, 'sold')
                    await create_order(
                        self.db, 
                        self.user_id,
                        offer.id,
                        g2g_order_data['order_id'],
                        'delivered'
                    )
                    
                    return {
                        'success': True,
                        'message': 'Order processed successfully',
                        'order_id': g2g_order_data['order_id']
                    }
                else:
                    # Если не удалось доставить - отменяем заказ
                    await cancel_order(g2g_api_key, g2g_secret, g2g_user_id, g2g_order_data['order_id'])
                    return {'error': 'Failed to deliver order'}
            else:
                # Если не удалось купить на LZT - отменяем заказ
                await cancel_order(g2g_api_key, g2g_secret, g2g_user_id, g2g_order_data['order_id'])
                await update_offer_status(self.db, offer.id, 'out_of_stock')
                return {'error': 'Failed to purchase account on LZT'}
                
        except Exception as e:
            # В случае ошибки отменяем заказ
            try:
                await cancel_order(g2g_api_key, g2g_secret, g2g_user_id, g2g_order_data['order_id'])
            except:
                pass
            return {'error': f'Processing error: {str(e)}'}
    
    async def check_order_status(self, order_id: str) -> Dict:
        """Проверяет статус заказа"""
        api_keys = await get_user_api_keys(self.db, self.user_id)
        if not api_keys:
            return {'error': 'API keys not found'}
        
        g2g_api_key = encryption_service.decrypt(api_keys.g2g_api_key)
        g2g_secret = encryption_service.decrypt(api_keys.g2g_secret)
        g2g_user_id = api_keys.g2g_user_id
        
        # Здесь будет запрос к G2G API для проверки статуса
        # Заглушка
        return {'status': 'delivered', 'order_id': order_id}