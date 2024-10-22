from telebot import types

matches = []  # Список матчей с индексами
current_match_index = 0  # Индекс текущего матча


# Функция для обработки игрового процесса
def handle_game_process(bot, message, match_schedule):
    global matches, current_match_index
    current_match_index = 0

    # Присваиваем индекс каждому матчу
    matches = [(index + 1, match[0], match[1]) for index, match in enumerate(match_schedule)]

    # Формируем строку для вывода сетки матчей
    response = "Расписание матчей:\n"
    for index, player1, player2 in matches:
        response += f"Игра {index}: {player1} vs {player2}\n"

    # Показываем кнопки: начать игру или пройти регистрацию заново
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Пройти регистрацию заново', 'Начать игру')

    # Отправляем расписание матчей в чат
    bot.send_message(message.chat.id, response)
    bot.send_message(message.chat.id, "Что вы хотите сделать дальше?", reply_markup=markup)


# Показ текущего матча и выбор победителя
def show_current_match(bot, chat_id):
    global current_match_index, matches
    if current_match_index >= len(matches):
        bot.send_message(chat_id, "Все игры завершены!")
        return

    match = matches[current_match_index]
    match_id, player1, player2 = match

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text=player1, callback_data=f"win_{player1}")
    button2 = types.InlineKeyboardButton(text=player2, callback_data=f"win_{player2}")
    markup.add(button1, button2)

    bot.send_message(chat_id, f"Игра {match_id}: {player1} vs {player2}\nВыберите победителя:", reply_markup=markup)


# Обработчик для выбора победителя
def handle_match_result(bot, call):
    global current_match_index
    winner = call.data.split('_')[1]
    bot.send_message(call.message.chat.id, f"Победитель: {winner}")

    current_match_index += 1

    # Проверяем, есть ли ещё матчи
    if current_match_index < len(matches):
        show_current_match(bot, call.message.chat.id)
    else:
        bot.send_message(call.message.chat.id, "Все игры завершены!")
