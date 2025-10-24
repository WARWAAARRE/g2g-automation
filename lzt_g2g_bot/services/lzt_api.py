import aiohttp
from config import config

async def test_lzt_connection(token: str) -> bool:
    """Проверка подключения к LZT API"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{config.LZT_API_URL}/market/me",
                headers=headers,
                timeout=10
            ) as response:
                return response.status == 200
                
    except Exception as e:
        print(f"LZT API Error: {e}")
        return False

async def get_lzt_accounts(category: str, params: dict, token: str) -> list:
    """Получение списка аккаунтов с LZT"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{config.LZT_API_URL}/market/{category}",
                headers=headers,
                params=params,
                timeout=10
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('items', [])
                return []
                
    except Exception as e:
        print(f"LZT API Error: {e}")
        return []

async def get_lzt_account_details(item_id: str, token: str) -> dict:
    """Получение деталей аккаунта"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{config.LZT_API_URL}/market/{item_id}",
                headers=headers,
                timeout=10
            ) as response:
                if response.status == 200:
                    return await response.json()
                return {}
                
    except Exception as e:
        print(f"LZT API Error: {e}")
        return {}