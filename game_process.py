import logging
from telebot import types

current_match_index = 0

def start_game(bot, chat_id, matches):
    global current_match_index
    current_match_index = 0
    if matches:
        show_current_match(bot, chat_id, matches)
    else:
        bot.send_message(chat_id, "Нет матчей для начала игры.")


def show_current_match(bot, chat_id, matches):
    global current_match_index
    if current_match_index >= len(matches):
        bot.send_message(chat_id, "Все матчи завершены!")
        logging.info(f"Все матчи завершены для чата {chat_id}.")
        return

    match = matches[current_match_index]
    player1, player2 = match[1], match[2]

    logging.info(f"Показываем матч {match[0]}: {player1} vs {player2} для чата {chat_id}.")

    # Создаем inline-кнопки для выбора победителя
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(f"{player1} победил", callback_data=f"win_{player1}")
    button2 = types.InlineKeyboardButton(f"{player2} победил", callback_data=f"win_{player2}")
    markup.add(button1, button2)

    bot.send_message(chat_id, f"Текущий матч: {player1} vs {player2}\nВыберите победителя:", reply_markup=markup)


def handle_match_result(bot, call, matches):
    global current_match_index

    winner = call.data.replace("win_", "")
    logging.info(f"Победитель выбран: {winner}")

    bot.answer_callback_query(call.id, f"Победитель: {winner}")
    bot.send_message(call.message.chat.id, f"Победитель: {winner}")

    # Переходим к следующему матчу
    current_match_index += 1
    show_current_match(bot, call.message.chat.id, matches)
