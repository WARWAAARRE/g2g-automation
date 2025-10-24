from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from database.crud import get_or_create_user
from utils.keyboards import get_main_menu_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    welcome_text = f"""👤 ДОБРО ПОЖАЛОВАТЬ В LZT → G2G БОТ!

🚀 Для начала работы нужно:

1. 🔑 Настроить API ключи
2. 💳 Выбрать тариф  
3. ⚙️ Настроить парсер

📋 Используйте кнопки ниже для навигации:

⚠️ Бот не хранит ваши данные в открытом виде"""
    
    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard())