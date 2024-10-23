import os
import logging
from telebot import TeleBot, types
from dotenv import load_dotenv
from registration import register_handlers
from game_process import start_game

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Загружаем переменные окружения из .env
load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
bot = TeleBot(API_TOKEN)

# Зарегистрированные игроки и матчи
players = []
matches = []

# Регистрируем обработчики команд
register_handlers(bot, players)

@bot.message_handler(commands=['start'])
def start_bot(message):
    reset_game_state()
    logging.info(f"Пользователь {message.from_user.id} начал регистрацию заново.")
    bot.send_message(message.chat.id, "Привет! Давайте начнём регистрацию игроков. Введите количество игроков:")
    bot.register_next_step_handler(message, get_player_count)

def reset_game_state():
    """Сбрасывает состояние игры и очищает списки игроков и матчей."""
    players.clear()
    matches.clear()

def get_player_count(message):
    try:
        count = int(message.text)
        if count < 2:
            bot.send_message(message.chat.id, "Нужно как минимум 2 игрока.")
            bot.register_next_step_handler(message, get_player_count)
            return
        bot.send_message(message.chat.id, f"Введите имена {count} игроков.")
        players_data = {'count': count, 'current': 0}
        bot.register_next_step_handler(message, lambda msg: get_player_names(msg, players_data))
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите число.")
        bot.register_next_step_handler(message, get_player_count)

def get_player_names(message, players_data):
    players.append(message.text)
    players_data['current'] += 1
    logging.info(f"Пользователь {message.from_user.id} добавил игрока: {message.text}")

    if players_data['current'] < players_data['count']:
        bot.send_message(message.chat.id, f"Введите имя игрока {players_data['current'] + 1}:")
        bot.register_next_step_handler(message, lambda msg: get_player_names(msg, players_data))
    else:
        logging.info(f"Пользователь {message.from_user.id} завершил регистрацию игроков: {players}")
        bot.send_message(message.chat.id, "Регистрация завершена!")
        show_options(message)

def show_options(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Пройти регистрацию заново', 'Сформировать сетку игр')
    logging.info(f"Пользователь {message.from_user.id} видит выбор: заново или сформировать сетку.")
    bot.send_message(message.chat.id, "Что вы хотите сделать дальше?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Пройти регистрацию заново')
def restart_registration(message):
    reset_game_state()
    logging.info(f"Пользователь {message.from_user.id} начал регистрацию заново.")
    bot.send_message(message.chat.id, "Введите количество игроков:")
    bot.register_next_step_handler(message, get_player_count)

@bot.message_handler(func=lambda message: message.text == 'Сформировать сетку игр')
def start_matches(message):
    if len(players) < 2:
        bot.reply_to(message, "Недостаточно игроков для формирования пар.")
        return

    global matches
    matches = [(i + 1, players[i % len(players)], players[(i + 1) % len(players)]) for i in range(len(players))]
    response = "Расписание матчей:\n"
    for match in matches:
        response += f"{match[0]}. {match[1]} vs {match[2]}\n"

    logging.info(f"Пользователь {message.from_user.id} сформировал сетку игр: {matches}")
    bot.send_message(message.chat.id, response)

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Начать игру', 'Пройти регистрацию заново')
    bot.send_message(message.chat.id, "Что вы хотите сделать дальше?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Начать игру')
def begin_game(message):
    logging.info(f"Пользователь {message.from_user.id} нажал кнопку 'Начать игру'.")
    start_game(bot, message.chat.id, matches)

if __name__ == "__main__":
    logging.info("Бот запущен и ожидает действий.")
    bot.polling(none_stop=True, interval=0)
