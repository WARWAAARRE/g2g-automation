import aiohttp
import hashlib
import hmac
from datetime import datetime
from config import config

def generate_g2g_signature(api_key: str, secret: str, user_id: str, endpoint: str = "/offers") -> str:
    """Генерация подписи для G2G API"""
    timestamp = str(int(datetime.now().timestamp() * 1000))
    canonical_string = endpoint + api_key + user_id + timestamp
    
    signature = hmac.new(
        key=bytes(secret.encode("utf8")),
        msg=bytes(canonical_string.encode("utf8")),
        digestmod=hashlib.sha256,
    ).hexdigest()
    
    return signature, timestamp

async def test_g2g_connection(api_key: str, secret: str, user_id: str) -> bool:
    """Проверка подключения к G2G API"""
    try:
        signature, timestamp = generate_g2g_signature(api_key, secret, user_id)
        
        headers = {
            "g2g-api-key": api_key,
            "g2g-user-id": user_id,
            "g2g-timestamp": timestamp,
            "g2g-signature": signature
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{config.G2G_API_URL}/offers",
                headers=headers,
                timeout=10
            ) as response:
                return response.status in [200, 201]
                
    except Exception as e:
        print(f"G2G API Error: {e}")
        return False

async def create_g2g_offer(api_key: str, secret: str, user_id: str, offer_data: dict) -> dict:
    """Создание оффера на G2G"""
    try:
        signature, timestamp = generate_g2g_signature(api_key, secret, user_id, "/offers")
        
        headers = {
            "g2g-api-key": api_key,
            "g2g-user-id": user_id,
            "g2g-timestamp": timestamp,
            "g2g-signature": signature,
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config.G2G_API_URL}/offers",
                headers=headers,
                json=offer_data,
                timeout=10
            ) as response:
                if response.status in [200, 201]:
                    return await response.json()
                return {}
                
    except Exception as e:
        print(f"G2G API Error: {e}")
        return {}