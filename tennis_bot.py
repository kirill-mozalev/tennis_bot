import os
from telebot import TeleBot, types
from dotenv import load_dotenv
from registration import register_handlers
from match_maker import get_match_schedule
from game_process import handle_game_process, show_current_match, handle_match_result  # Добавили функцию обработки результата игры

# Загружаем переменные окружения из .env
load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
bot = TeleBot(API_TOKEN)

# Зарегистрированные игроки
players = []

# Регистрируем обработчики команд
register_handlers(bot, players)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_bot(message):
    """
    Сбрасываем все данные и начинаем диалог с самого начала.
    """
    players.clear()  # Очищаем список игроков
    bot.send_message(message.chat.id, "Привет! Давайте начнём регистрацию игроков. Введите количество игроков:")
    bot.register_next_step_handler(message, get_player_count)


# Логика для обработки ввода количества игроков
def get_player_count(message):
    try:
        count = int(message.text)
        if count < 2:
            bot.send_message(message.chat.id, "Нужно как минимум 2 игрока.")
            bot.register_next_step_handler(message, get_player_count)
            return

        bot.send_message(message.chat.id, f"Введите имена {count} игроков.")
        players_data = {
            'count': count,
            'current': 0
        }
        bot.register_next_step_handler(message, lambda msg: get_player_names(msg, players_data))
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите число.")
        bot.register_next_step_handler(message, get_player_count)


# Логика для сбора имён игроков
def get_player_names(message, players_data):
    players.append(message.text)
    players_data['current'] += 1

    if players_data['current'] < players_data['count']:
        bot.send_message(message.chat.id, f"Введите имя игрока {players_data['current'] + 1}:")
        bot.register_next_step_handler(message, lambda msg: get_player_names(msg, players_data))
    else:
        bot.send_message(message.chat.id, "Регистрация завершена!")
        show_options(message)


# Показываем кнопки после регистрации
def show_options(message):
    """
    Показывает кнопки для выбора: начать заново или сформировать сетку игр.
    """
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Пройти регистрацию заново', 'Сформировать сетку игр')

    bot.send_message(message.chat.id, "Что вы хотите сделать дальше?", reply_markup=markup)


# Обработчик для кнопки "Пройти регистрацию заново"
@bot.message_handler(func=lambda message: message.text == 'Пройти регистрацию заново')
def restart_registration(message):
    players.clear()  # Очищаем список игроков
    bot.send_message(message.chat.id, "Регистрация начата заново.")
    bot.send_message(message.chat.id, "Введите количество игроков:")
    bot.register_next_step_handler(message, get_player_count)


# Обработчик для кнопки "Сформировать сетку игр"
@bot.message_handler(func=lambda message: message.text == 'Сформировать сетку игр')
def start_matches(message):
    if len(players) < 2:
        bot.reply_to(message, "Недостаточно игроков для формирования пар.")
        return

    match_schedule = get_match_schedule(players)

    if not match_schedule:
        bot.reply_to(message, "Произошла ошибка при создании расписания.")
        return

    # Передаём управление игровому процессу
    handle_game_process(bot, message, match_schedule)


# Обработчик для кнопки "Начать игру"
@bot.message_handler(func=lambda message: message.text == 'Начать игру')
def begin_game(message):
    # Показываем первый матч
    show_current_match(bot, message.chat.id)


# Обработчик callback для выбора победителя
@bot.callback_query_handler(func=lambda call: call.data.startswith("win_"))
def callback_winner(call):
    handle_match_result(bot, call)  # Передаём в функцию обработки результата


# Запуск бота
if __name__ == "__main__":
    print("Бот запущен")
    bot.polling(none_stop=True)
