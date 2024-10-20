from telebot import TeleBot, types

# Храним временные данные для регистрации
players_data = {}

def register_handlers(bot: TeleBot):
    # Обработчик команды /start
    @bot.message_handler(commands=['start'])
    def start_message(message: types.Message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton("Начать регистрацию")
        markup.add(button)
        bot.send_message(message.chat.id, "Привет! Нажми на кнопку ниже, чтобы начать регистрацию игроков.", reply_markup=markup)

    # Начинаем регистрацию
    @bot.message_handler(func=lambda message: message.text == "Начать регистрацию")
    def start_registration(message: types.Message):
        bot.send_message(message.chat.id, "Введите количество игроков:")
        bot.register_next_step_handler(message, process_player_count)

    # Обрабатываем ввод количества игроков
    def process_player_count(message: types.Message):
        try:
            player_count = int(message.text)
            if player_count < 2:
                bot.send_message(message.chat.id, "Количество игроков должно быть не меньше 2. Введите снова:")
                bot.register_next_step_handler(message, process_player_count)
                return
            # Сохраняем количество игроков в словарь
            players_data[message.chat.id] = {'count': player_count, 'players': []}
            bot.send_message(message.chat.id, f"Ок! Теперь вводите имена игроков. Введите имя игрока 1:")
            bot.register_next_step_handler(message, process_player_name)
        except ValueError:
            bot.send_message(message.chat.id, "Введите числовое значение для количества игроков.")
            bot.register_next_step_handler(message, process_player_count)

    # Обрабатываем ввод имен игроков
    def process_player_name(message: types.Message):
        chat_id = message.chat.id
        if chat_id in players_data:
            players_info = players_data[chat_id]
            players_info['players'].append(message.text)
            if len(players_info['players']) < players_info['count']:
                bot.send_message(chat_id, f"Имя игрока {len(players_info['players']) + 1}:")
                bot.register_next_step_handler(message, process_player_name)
            else:
                player_list = ", ".join(players_info['players'])
                bot.send_message(chat_id, f"Все игроки зарегистрированы: {player_list}.\nНажмите 'Подтвердить', чтобы закончить.")
                confirm_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                confirm_button = types.KeyboardButton("Подтвердить")
                confirm_markup.add(confirm_button)
                bot.send_message(chat_id, "Подтвердите регистрацию.", reply_markup=confirm_markup)
                bot.register_next_step_handler(message, confirm_registration)

    # Обрабатываем подтверждение регистрации
    def confirm_registration(message: types.Message):
        chat_id = message.chat.id
        if message.text == "Подтвердить" and chat_id in players_data:
            players_info = players_data[chat_id]
            player_list = ", ".join(players_info['players'])
            bot.send_message(chat_id, f"Регистрация завершена. Игроки: {player_list}")
            del players_data[chat_id]  # Удаляем данные после завершения регистрации
        else:
            bot.send_message(chat_id, "Выберите 'Подтвердить' для завершения регистрации.")
