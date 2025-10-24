import asyncio
from typing import List, Dict
from services.lzt_api import get_lzt_accounts, get_lzt_account_details
from services.g2g_api import create_g2g_offer
from services.encryption import encryption_service
from database.crud import get_user_api_keys, get_user_settings
from templates.steam import create_steam_offer
from templates.valorant import create_valorant_offer
# ... остальные шаблоны

class ParsingService:
    def __init__(self, db, user_id: int):
        self.db = db
        self.user_id = user_id
        self.found_accounts = []
    
    async def run_parsing(self) -> List[Dict]:
        """Основной метод парсинга"""
        # Получаем настройки и ключи пользователя
        settings = await get_user_settings(self.db, self.user_id)
        api_keys = await get_user_api_keys(self.db, self.user_id)
        
        if not settings or not api_keys:
            return []
        
        # Дешифруем токены
        lzt_token = encryption_service.decrypt(api_keys.lzt_token)
        g2g_api_key = encryption_service.decrypt(api_keys.g2g_api_key)
        g2g_secret = encryption_service.decrypt(api_keys.g2g_secret)
        
        # Парсим выбранные категории
        categories = eval(settings.parser_categories) if settings.parser_categories else []
        
        for category in categories:
            accounts = await self.parse_category(category, settings, lzt_token)
            self.found_accounts.extend(accounts)
        
        return self.found_accounts
    
    async def parse_category(self, category: str, settings, lzt_token: str) -> List[Dict]:
        """Парсинг конкретной категории"""
        params = {
            "pmin": settings.price_min,
            "pmax": settings.price_max,
            "title": "",  # Можно добавить поиск по ключевым словам
            "parse_sticky_items": True
        }
        
        accounts = await get_lzt_accounts(category, params, lzt_token)
        processed_accounts = []
        
        for account in accounts[:10]:  # Ограничиваем для теста
            # Получаем детали аккаунта
            details = await get_lzt_account_details(account['item_id'], lzt_token)
            
            # Применяем фильтры
            if self.apply_filters(details, settings):
                processed_account = await self.process_account(details, settings)
                processed_accounts.append(processed_account)
        
        return processed_accounts
    
    def apply_filters(self, account_details: Dict, settings) -> bool:
        """Применяет фильтры к аккаунту"""
        # Здесь будет логика фильтрации по отлежке, давности и т.д.
        return True  # Заглушка
    
    async def process_account(self, account_details: Dict, settings) -> Dict:
        """Обрабатывает аккаунт и готовит для G2G"""
        # Определяем тип аккаунта и выбираем шаблон
        category = account_details.get('category', {}).get('name', '').lower()
        
        if 'steam' in category:
            template_data = create_steam_offer(account_details, settings.markup_percent)
        elif 'valorant' in category:
            template_data = create_valorant_offer(account_details, settings.markup_percent)
        # ... остальные категории
        
        return {
            'lzt_data': account_details,
            'g2g_template': template_data,
            'price': self.calculate_price(account_details.get('price', 0), settings.markup_percent)
        }
    
    def calculate_price(self, original_price: float, markup_percent: int) -> float:
        """Рассчитывает цену с наценкой"""
        return round(original_price * (1 + markup_percent / 100), 2)

async def run_parsing(user_id: int, settings, api_keys) -> List[Dict]:
    """Запуск парсинга для пользователя"""
    # Заглушка - здесь будет реальная логика
    return [
        {
            'title': 'Steam 50 games / 15 Level',
            'price': 25.99,
            'category': 'Steam',
            'description': 'Test account description...'
        }
    ]