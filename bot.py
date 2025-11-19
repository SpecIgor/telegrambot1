import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- КОНФИГУРАЦИЯ ---
# Вставьте сюда токен, полученный от @BotFather
BOT_TOKEN = "8456930259:AAEmlOpQYgcMbG_zOO3qcYENZfJo7VnQfVE"

# ID канала, на который нужно подписаться (обязательно начните с -100 для публичных каналов или используйте ID)
# Бот должен быть АДМИНИСТРАТОРОМ в этом канале, чтобы проверять подписку!
CHANNEL_ID = "@timurelgohary" # Или числовой ID, например -100123456789
CHANNEL_URL = "https://t.me/timurelgohary" # Ссылка для кнопки

# Список лид-магнитов
# type: 'link' (ссылка), 'text' (текст), 'file_id' (если файл уже загружен в ТГ)
LEAD_MAGNETS = {
    "magnet_1": {
        "title": "📚 Чек-лист защита от дипфейков",
        "type": "link",
        "content": "https://radiant-gingersnap-e34b63.netlify.app",
        "description": "Пошаговый план для запуска вашего проекта."
    },
    "magnet_2": {
        "title": "📚 Чек-лист 2",
        "type": "link", # Можно заменить на отправку видео
        "content": "https://docs.google.com",
        "description": "Секреты монтажа для Shorts за 5 минут."
    },
    "magnet_3": {
        "title": "📚 Чек-лист 3",
        "type": "text",
        "content": "Вот ваша ссылка на Google Таблицу: https://docs.google.com/spreadsheets/...",
        "description": "Шаблон для учета финансов."
    }
}

# --- ИНИЦИАЛИЗАЦИЯ ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# --- ФУНКЦИИ ---

async def check_subscription(user_id: int) -> bool:
    """Проверяет, подписан ли пользователь на канал."""
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        # Статусы: creator (создатель), administrator (админ), member (участник)
        if member.status in ["creator", "administrator", "member"]:
            return True
        return False
    except Exception as e:
        logging.error(f"Ошибка проверки подписки: {e}")
        # Если бот не админ или ID канала неверен, лучше пустить пользователя, чем блокировать
        return False

def get_subscription_keyboard():
    """Клавиатура с просьбой подписаться."""
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="👉 Подписаться на канал", url=CHANNEL_URL))
    keyboard.row(InlineKeyboardButton(text="✅ Я подписался!", callback_data="check_sub"))
    return keyboard.as_markup()

def get_magnets_keyboard():
    """Клавиатура со списком лид-магнитов."""
    keyboard = InlineKeyboardBuilder()
    for key, data in LEAD_MAGNETS.items():
        keyboard.row(InlineKeyboardButton(text=data["title"], callback_data=f"get_{key}"))
    return keyboard.as_markup()

# --- ХЕНДЛЕРЫ (ОБРАБОТЧИКИ) ---

@dp.message(CommandStart())
async def start_command(message: types.Message):
    """Обработка команды /start."""
    user_name = message.from_user.first_name
    
    welcome_text = (
        f"Привет, {user_name}! 👋\n\n"
        f"Я подготовил для тебя крутые материалы.\n"
        f"Чтобы получить доступ к **секретной базе знаний**, подпишись на мой канал."
    )
    
    await message.answer(welcome_text, reply_markup=get_subscription_keyboard())

@dp.callback_query(F.data == "check_sub")
async def process_check_sub(callback: types.CallbackQuery):
    """Нажатие на кнопку 'Я подписался'."""
    is_subscribed = await check_subscription(callback.from_user.id)
    
    if is_subscribed:
        await callback.message.edit_text(
            "✅ Подписка подтверждена!\n\n"
            "Выбери, какой материал ты хочешь забрать прямо сейчас:",
            reply_markup=get_magnets_keyboard()
        )
    else:
        await callback.answer("❌ Вы еще не подписались!", show_alert=True)

@dp.callback_query(F.data.startswith("get_"))
async def process_get_magnet(callback: types.CallbackQuery):
    """Выдача конкретного лид-магнита."""
    magnet_key = callback.data.replace("get_", "")
    magnet_data = LEAD_MAGNETS.get(magnet_key)
    
    # Повторная проверка подписки (на случай, если человек отписался и нажал старую кнопку)
    if not await check_subscription(callback.from_user.id):
        await callback.message.answer("⚠️ Кажется, вы не подписаны. Подпишитесь, чтобы скачать файл.", reply_markup=get_subscription_keyboard())
        return

    if not magnet_data:
        await callback.answer("Ошибка: материал не найден.")
        return

    # Логика выдачи в зависимости от типа
    if magnet_data["type"] == "link":
        await callback.message.answer(
            f"🎁 <b>{magnet_data['title']}</b>\n\n"
            f"{magnet_data['description']}\n\n"
            f"🔗 Ссылка: {magnet_data['content']}",
            parse_mode="HTML"
        )
    elif magnet_data["type"] == "text":
        await callback.message.answer(magnet_data['content'])
    
    # Пример отправки файла (если бы у вас был ID файла или локальный путь)
    # elif magnet_data["type"] == "file":
    #     await callback.message.answer_document(document=magnet_data['content'], caption=magnet_data['title'])

    await callback.answer() # Убираем часики загрузки

# --- ЗАПУСК ---
async def main():
    print("Бот запущен...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())