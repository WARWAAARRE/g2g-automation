from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.crud import get_or_create_user, save_lzt_token, save_g2g_keys, get_user_api_keys
from services.lzt_api import test_lzt_connection
from services.g2g_api import test_g2g_connection
from services.encryption import encryption_service
from utils.keyboards import get_api_setup_keyboard, get_back_keyboard

router = Router()

class APIStates(StatesGroup):
    waiting_lzt_token = State()
    waiting_g2g_api_key = State()
    waiting_g2g_secret = State()
    waiting_g2g_user_id = State()

@router.message(F.text == "🔑 НАСТРОИТЬ API КЛЮЧИ")
async def api_setup_menu(message: Message):
    """Меню настройки API ключей"""
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
    api_keys = await get_user_api_keys(user[0])  # user[0] - это id
    
    status_text = "📊 СТАТУС API:\n"
    
    if api_keys and api_keys[2]:  # api_keys[2] - lzt_token
        status_text += "✅ LZT API: Настроено\n"
    else:
        status_text += "❌ LZT API: Не настроено\n"
        
    if api_keys and api_keys[3]:  # api_keys[3] - g2g_api_key
        status_text += "✅ G2G API: Настроено\n"
    else:
        status_text += "❌ G2G API: Не настроено\n"

    menu_text = f"""
🔑 НАСТРОЙКА API КЛЮЧЕЙ

{status_text}
Выберите что настроить:
"""
    await message.answer(menu_text, reply_markup=get_api_setup_keyboard())

@router.callback_query(F.data == "setup_lzt")
async def setup_lzt_start(callback: CallbackQuery, state: FSMContext):
    """Начало настройки LZT API"""
    instruction_text = """
🔑 НАСТРОЙКА LZT API

📝 Инструкция:
1. Перейдите: https://zelenka.guru/account/api
2. Создайте OAuth Token
3. Выберите права: Market API
4. Скопируйте токен ниже

🔐 Введите ваш LZT Token:
"""
    await callback.message.edit_text(instruction_text)
    await callback.message.answer("Ожидаю ваш токен...", reply_markup=get_back_keyboard())
    await state.set_state(APIStates.waiting_lzt_token)
    await callback.answer()

@router.message(APIStates.waiting_lzt_token)
async def process_lzt_token(message: Message, state: FSMContext):
    """Обработка LZT токена"""
    token = message.text.strip()
    
    # Проверяем токен
    is_valid = await test_lzt_connection(token)
    
    if is_valid:
        user = await get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        # Шифруем и сохраняем токен
        encrypted_token = encryption_service.encrypt(token)
        await save_lzt_token(user[0], encrypted_token)
    
        success_text = """
✅ LZT API УСПЕШНО НАСТРОЕНО!

Токен проверен и сохранен в зашифрованном виде.
"""
        await message.answer(success_text)
        await api_setup_menu(message)
    else:
        error_text = """
❌ НЕВЕРНЫЙ LZT TOKEN

Проверьте:
• Правильность введенного токена
• Наличие прав Market API
• Активность токена

Попробуйте еще раз:
"""
        await message.answer(error_text, reply_markup=get_back_keyboard())
    
    await state.clear()

@router.callback_query(F.data == "setup_g2g")
async def setup_g2g_start(callback: CallbackQuery, state: FSMContext):
    """Начало настройки G2G API"""
    instruction_text = """
🔑 НАСТРОЙКА G2G API

📝 Инструкция:
1. Перейдите в G2G Account → API Management
2. Создайте API Keys
3. Скопируйте данные ниже

🔐 Введите ваш G2G API Key:
"""
    await callback.message.edit_text(instruction_text)
    await callback.message.answer("Ожидаю API Key...", reply_markup=get_back_keyboard())
    await state.set_state(APIStates.waiting_g2g_api_key)
    await callback.answer()

@router.message(APIStates.waiting_g2g_api_key)
async def process_g2g_api_key(message: Message, state: FSMContext):
    """Обработка G2G API Key"""
    api_key = message.text.strip()
    await state.update_data(g2g_api_key=api_key)
    
    await message.answer("🔐 Теперь введите G2G Secret Key:", reply_markup=get_back_keyboard())
    await state.set_state(APIStates.waiting_g2g_secret)

@router.message(APIStates.waiting_g2g_secret)
async def process_g2g_secret(message: Message, state: FSMContext):
    """Обработка G2G Secret Key"""
    secret = message.text.strip()
    await state.update_data(g2g_secret=secret)
    
    await message.answer("👤 Теперь введите G2G User ID:", reply_markup=get_back_keyboard())
    await state.set_state(APIStates.waiting_g2g_user_id)

@router.message(APIStates.waiting_g2g_user_id)
async def process_g2g_user_id(message: Message, state: FSMContext):
    """Обработка G2G User ID и сохранение всех данных"""
    user_id = message.text.strip()
    data = await state.get_data()
    
    api_key = data.get('g2g_api_key')
    secret = data.get('g2g_secret')
    
    # Проверяем G2G подключение
    is_valid = await test_g2g_connection(api_key, secret, user_id)
    
    if is_valid:
        user = await get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        # Шифруем и сохраняем ключи
        encrypted_api_key = encryption_service.encrypt(api_key)
        encrypted_secret = encryption_service.encrypt(secret)
        
        await save_g2g_keys(user[0], encrypted_api_key, encrypted_secret, user_id)
    
        success_text = """
✅ G2G API УСПЕШНО НАСТРОЕНО!

Все ключи проверены и сохранены в зашифрованном виде.
"""
        await message.answer(success_text)
        await api_setup_menu(message)
    else:
        error_text = """
❌ ОШИБКА ПОДКЛЮЧЕНИЯ G2G API

Проверьте:
• Правильность API Key и Secret
• Активность API ключей
• Правильность User ID

Попробуйте еще раз:
"""
        await message.answer(error_text, reply_markup=get_back_keyboard())
    
    await state.clear()

@router.callback_query(F.data == "check_all_apis")
async def check_all_apis(callback: CallbackQuery):
    """Проверка всех API подключений"""
    user = await get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name
    )
    
    api_keys = await get_user_api_keys(user[0])
    status_text = "🔍 ПРОВЕРКА API ПОДКЛЮЧЕНИЙ:\n\n"
    
    if api_keys and api_keys[2]:  # lzt_token
        try:
            decrypted_token = encryption_service.decrypt(api_keys[2])
            lzt_valid = await test_lzt_connection(decrypted_token)
            status_text += "✅ LZT API: Работает\n" if lzt_valid else "❌ LZT API: Ошибка\n"
        except:
            status_text += "❌ LZT API: Ошибка дешифровки\n"
    else:
        status_text += "❌ LZT API: Не настроено\n"
        
    if api_keys and api_keys[3]:  # g2g_api_key
        try:
            decrypted_api_key = encryption_service.decrypt(api_keys[3])
            decrypted_secret = encryption_service.decrypt(api_keys[4])
            g2g_valid = await test_g2g_connection(decrypted_api_key, decrypted_secret, api_keys[5])
            status_text += "✅ G2G API: Работает\n" if g2g_valid else "❌ G2G API: Ошибка\n"
        except:
            status_text += "❌ G2G API: Ошибка дешифровки\n"
    else:
        status_text += "❌ G2G API: Не настроено\n"
    
    await callback.message.edit_text(status_text, reply_markup=get_api_setup_keyboard())
    await callback.answer()

@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    """Возврат в главное меню"""
    from handlers.start import cmd_start
    await cmd_start(callback.message)
    await callback.answer()

@router.callback_query(F.data == "api_setup")
async def back_to_api_setup(callback: CallbackQuery):
    """Возврат в меню API"""
    await api_setup_menu(callback.message)
    await callback.answer()