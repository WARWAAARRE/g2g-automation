from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from config import config

class EncryptionService:
    def __init__(self):
        self.key = self._generate_key()
    
    def _generate_key(self) -> bytes:
        """Генерирует ключ шифрования на основе ENCRYPTION_KEY"""
        password = config.ENCRYPTION_KEY.encode()
        salt = b'lzt_g2g_bot_salt_2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password))
    
    def encrypt(self, data: str) -> str:
        """Шифрует данные"""
        fernet = Fernet(self.key)
        encrypted = fernet.encrypt(data.encode())
        return encrypted.decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Расшифровывает данные"""
        fernet = Fernet(self.key)
        decrypted = fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()

encryption_service = EncryptionService()