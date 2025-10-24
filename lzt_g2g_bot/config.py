import os
from dataclasses import dataclass, field
from typing import List

@dataclass
class Config:
    BOT_TOKEN: str = "8185424205:AAGt7b0HLvZ3QS3W4UE_wZP2SQhoM2B-gNA"
    
    # Исправляем ADMIN_IDS с field
    ADMIN_IDS: List[int] = field(default_factory=lambda: [5670428160])
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///database.db"
    
    # Encryption
    ENCRYPTION_KEY: str = "G3ld45FLGSLFGgg"
    
    # API URLs
    LZT_API_URL: str = "https://api.zelenka.guru"
    G2G_API_URL: str = "https://api.g2g.com"

config = Config()