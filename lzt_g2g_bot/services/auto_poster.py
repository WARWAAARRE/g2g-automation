import asyncio
from typing import List, Dict
from services.lzt_api import get_lzt_accounts, get_lzt_account_details
from services.g2g_api import create_g2g_offer
from services.encryption import encryption_service
from database.crud import get_user_api_keys, get_user_settings, create_user_offer, get_user_active_offers
from templates.steam import create_steam_offer
from templates.valorant import create_valorant_offer
from templates.lol import create_lol_offer
from templates.genshin import create_genshin_offer
from templates.honkai import create_honkai_offer
from templates.zzz import create_zzz_offer
from templates.minecraft import create_minecraft_offer
from templates.brawl_stars import create_brawl_stars_offer
from templates.clash_of_clans import create_clash_of_clans_offer

class AutoPoster:
    def __init__(self, db, user_id: int):
        self.db = db
        self.user_id = user_id
        self.stats = {
            'parsed': 0,
            'posted': 0,
            'errors': 0
        }
    
    async def run_auto_posting(self) -> Dict:
        """Запуск автоматического создания объявлений"""
        # Получаем настройки и ключи
        settings = await get_user_settings(self.db, self.user_id)
        api_keys = await get_user_api_keys(self.db, self.user_id)
        
        if not settings or not api_keys:
            return self.stats
        
        # Проверяем лимиты тарифа
        active_offers = await get_user_active_offers(self.db, self.user_id)
        if len(active_offers) >= self.get_daily_limit(settings.subscription_type):
            return {'error': 'Достигнут дневной лимит объявлений'}
        
        # Дешифруем ключи
        lzt_token = encryption_service.decrypt(api_keys.lzt_token)
        g2g_api_key = encryption_service.decrypt(api_keys.g2g_api_key)
        g2g_secret = encryption_service.decrypt(api_keys.g2g_secret)
        g2g_user_id = api_keys.g2g_user_id
        
        # Парсим аккаунты с LZT
        categories = eval(settings.parser_categories) if settings.parser_categories else []
        
        for category in categories:
            await self.process_category(category, settings, lzt_token, g2g_api_key, g2g_secret, g2g_user_id)
        
        return self.stats
    
    async def process_category(self, category: str, settings, lzt_token: str, 
                            g2g_api_key: str, g2g_secret: str, g2g_user_id: str):
        """Обрабатывает категорию и создает объявления"""
        params = {
            "pmin": settings.price_min,
            "pmax": settings.price_max,
            "parse_sticky_items": True
        }
        
        accounts = await get_lzt_accounts(category, params, lzt_token)
        self.stats['parsed'] += len(accounts)
        
        for account in accounts[:5]:  # Ограничиваем для начала
            if self.stats['posted'] >= 3:  # Максимум 3 объявления за раз
                break
                
            try:
                # Получаем детали аккаунта
                details = await get_lzt_account_details(account['item_id'], lzt_token)
                
                # Применяем фильтры
                if not self.apply_filters(details, settings):
                    continue
                
                # Создаем шаблон для G2G
                template = self.create_offer_template(details, settings.markup_percent)
                if not template:
                    continue
                
                # Создаем объявление на G2G
                result = await create_g2g_offer(g2g_api_key, g2g_secret, g2g_user_id, template['offer_data'])
                
                if result:
                    # Сохраняем в БД
                    await create_user_offer(
                        self.db, 
                        self.user_id,
                        details['item_id'],
                        result.get('id'),
                        template['title'],
                        template['price'],
                        category
                    )
                    self.stats['posted'] += 1
                else:
                    self.stats['errors'] += 1
                    
                await asyncio.sleep(2)  # Задержка между запросами
                
            except Exception as e:
                print(f"Error processing account: {e}")
                self.stats['errors'] += 1
                continue
    
    def apply_filters(self, account_details: Dict, settings) -> bool:
        """Применяет фильтры к аккаунту"""
        # Фильтр по отлежке
        last_activity = account_details.get('last_activity')
        if last_activity and settings.last_activity_filter != 'any':
            # Логика проверки отлежки
            pass
        
        # Фильтр по давности выставления
        created_time = account_details.get('created_time')
        if created_time and settings.account_age_filter != 'any':
            # Логика проверки давности
            pass
        
        return True
    
    def create_offer_template(self, account_details: Dict, markup_percent: int) -> Dict:
        """Создает шаблон объявления в зависимости от категории"""
        category_name = account_details.get('category', {}).get('name', '').lower()
        
        if 'steam' in category_name:
            return create_steam_offer(account_details, markup_percent)
        elif 'valorant' in category_name:
            return create_valorant_offer(account_details, markup_percent)
        elif 'league' in category_name or 'lol' in category_name:
            return create_lol_offer(account_details, markup_percent)
        elif 'genshin' in category_name:
            return create_genshin_offer(account_details, markup_percent)
        elif 'honkai' in category_name:
            return create_honkai_offer(account_details, markup_percent)
        elif 'zenless' in category_name:
            return create_zzz_offer(account_details, markup_percent)
        elif 'minecraft' in category_name:
            return create_minecraft_offer(account_details, markup_percent)
        elif 'brawl' in category_name:
            return create_brawl_stars_offer(account_details, markup_percent)
        elif 'clash' in category_name:
            return create_clash_of_clans_offer(account_details, markup_percent)
        
        return None
    
    def get_daily_limit(self, subscription_type: str) -> int:
        """Возвращает дневной лимит по тарифу"""
        limits = {
            'basic': 20,
            'premium': 50,
            'pro': 100,
            'owner': 9999
        }
        return limits.get(subscription_type, 20)