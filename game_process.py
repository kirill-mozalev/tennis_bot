import logging
from telebot import types

def start_game(bot, chat_id, matches):
    current_match_index = 0
    if matches:
        show_current_match(bot, chat_id, matches, current_match_index)
    else:
        bot.send_message(chat_id, "Нет матчей для начала игры.")

def show_current_match(bot, chat_id, matches, current_match_index):
    if current_match_index >= len(matches):
        bot.send_message(chat_id, "Все матчи завершены!")
        logging.info(f"Все матчи завершены для чата {chat_id}.")
        return

    match = matches[current_match_index]
    player1, player2 = match[1], match[2]

    logging.info(f"Показываем матч {match[0]}: {player1} vs {player2} для чата {chat_id}.")

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button1 = types.KeyboardButton(f"{player1} победил")
    button2 = types.KeyboardButton(f"{player2} победил")
    markup.add(button1, button2)

    bot.send_message(chat_id, f"Текущий матч: {player1} vs {player2}\nВыберите победителя:", reply_markup=markup)

    # Запрашиваем результат матча
    bot.register_next_step_handler_by_chat_id(chat_id, lambda message: handle_match_result(bot, message, matches, current_match_index))

def handle_match_result(bot, message, matches, current_match_index):
    winner = message.text.replace(" победил", "")
    logging.info(f"Победитель выбран: {winner}")

    bot.send_message(message.chat.id, f"Победитель: {winner}")

    # Переходим к следующему матчу
    current_match_index += 1
    show_current_match(bot, message.chat.id, matches, current_match_index)
