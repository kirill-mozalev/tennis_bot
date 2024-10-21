from telebot import types

def register_handlers(bot, players):
    @bot.message_handler(commands=['register'])
    def start_registration(message):
        players.clear()  # Очищаем список игроков перед началом новой регистрации
        bot.send_message(message.chat.id, "Введите количество игроков:")

        bot.register_next_step_handler(message, get_player_count)

    def get_player_count(message):
        try:
            count = int(message.text)
            if count < 2:
                bot.send_message(message.chat.id, "Нужно как минимум 2 игрока.")
                return

            bot.send_message(message.chat.id, f"Введите имена {count} игроков.")
            players_data = {
                'count': count,
                'current': 0
            }
            bot.register_next_step_handler(message, lambda msg: get_player_names(msg, players_data))
        except ValueError:
            bot.send_message(message.chat.id, "Пожалуйста, введите число.")

    def get_player_names(message, players_data):
        players.append(message.text)
        players_data['current'] += 1

        if players_data['current'] < players_data['count']:
            bot.send_message(message.chat.id, f"Введите имя игрока {players_data['current'] + 1}:")
            bot.register_next_step_handler(message, lambda msg: get_player_names(msg, players_data))
        else:
            bot.send_message(message.chat.id, "Регистрация завершена!")
            show_options(message)

    def show_options(message):
        """
        Показывает кнопки для выбора: начать заново или сформировать сетку игр.
        """
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add('Пройти регистрацию заново', 'Сформировать сетку игр')

        bot.send_message(message.chat.id, "Что вы хотите сделать дальше?", reply_markup=markup)
