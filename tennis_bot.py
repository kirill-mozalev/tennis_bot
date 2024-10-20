import os
from telebot import TeleBot
from dotenv import load_dotenv
from registration import register_handlers

# Загружаем переменные окружения из .env
load_dotenv()

# Получаем токен из переменных окружения
API_TOKEN = os.getenv("BOT_TOKEN")

# Инициализация бота
bot = TeleBot(API_TOKEN)

# Регистрируем обработчики из модуля регистрации
register_handlers(bot)

# Запускаем бота
if __name__ == "__main__":
    print("Бот запущен")
    bot.polling(none_stop=True)
