import logging
from telebot import types
from tournament import Tournament  # Импортируем класс из tournament.py

# Создаем объект турнира
tournament = Tournament()


def start_registration(bot, chat_id):
    """Начинает новую регистрацию и сбрасывает статистику."""
    reset_tournament()
    bot.send_message(chat_id, "Начата новая регистрация. Пожалуйста, добавьте игроков.")


def start_game(bot, chat_id, matches):
    """Запускает новый турнир и отображает первый матч."""
    tournament.set_matches(matches)
    if tournament.get_current_match():
        show_current_match(bot, chat_id)
    else:
        bot.send_message(chat_id, "Нет матчей для начала игры.")


def show_current_match(bot, chat_id):
    """Отображает текущий матч и кнопки для выбора победителя."""
    match = tournament.get_current_match()
    if not match:
        bot.send_message(chat_id, "Все матчи завершены!")
        end_round(bot, chat_id)
        return

    match_number, player1, player2 = match
    logging.info(f"Показываем матч {match_number}: {player1} vs {player2} для чата {chat_id}.")

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button1 = types.KeyboardButton(f"{player1} победил")
    button2 = types.KeyboardButton(f"{player2} победил")
    markup.add(button1, button2)

    bot.send_message(chat_id, f"Текущий матч: {player1} vs {player2}\nВыберите победителя:", reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(chat_id, lambda message: handle_match_result(bot, message))


def handle_match_result(bot, message):
    """Обрабатывает выбор победителя и отображает следующий матч или завершает круг."""
    winner = message.text.replace(" победил", "")
    tournament.add_win(winner)  # Обновляем статистику побед
    logging.info(f"Победитель выбран: {winner}")

    bot.send_message(message.chat.id, f"Победитель: {winner}")
    tournament.increment_match_index()

    if tournament.is_tournament_finished():
        end_round(bot, message.chat.id)
    else:
        show_current_match(bot, message.chat.id)


def end_round(bot, chat_id):
    """Завершает текущий круг и отображает статистику."""
    round_results = dict(sorted(tournament.get_round_results().items(), key=lambda item: item[1], reverse=True))
    total_results = dict(sorted(tournament.get_total_results().items(), key=lambda item: item[1], reverse=True))

    # Вывод статистики текущего круга
    round_message = "Статистика текущего круга:\n" + "\n".join(
        [f"{player}: {wins} побед" for player, wins in round_results.items()]
    )
    bot.send_message(chat_id, round_message)

    # Вывод общей статистики
    total_message = "Общая статистика побед за все круги:\n" + "\n".join(
        [f"{player}: {wins} побед" for player, wins in total_results.items()]
    )
    bot.send_message(chat_id, total_message)

    # Кнопки для нового круга или завершения игры
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Начать новый круг', 'Завершить игру на сегодня')
    bot.send_message(chat_id, "Что вы хотите сделать дальше?", reply_markup=markup)

    # Очищаем статистику текущего круга
    tournament.round_results = {player: 0 for player in tournament.players}
    bot.register_next_step_handler_by_chat_id(chat_id, lambda message: handle_post_round_choice(bot, message))


def handle_post_round_choice(bot, message):
    """Обрабатывает выбор пользователя после завершения круга."""
    if message.text == 'Начать новый круг':
        logging.info("Начинаем новый круг.")
        start_game(bot, message.chat.id, tournament.matches)  # Начинаем новый круг с той же сеткой
    elif message.text == 'Завершить игру на сегодня':
        # Получаем и сортируем общую статистику перед завершением
        total_results = dict(sorted(tournament.get_total_results().items(), key=lambda item: item[1], reverse=True))
        total_message = "Общая статистика побед за все круги:\n" + "\n".join(
            [f"{player}: {wins} побед" for player, wins in total_results.items()]
        )
        bot.send_message(message.chat.id, total_message)

        # Сообщение о завершении игры
        bot.send_message(message.chat.id, "Игра завершена. Спасибо за участие!")
        logging.info("Игра завершена пользователем.")
    else:
        bot.send_message(
            message.chat.id,
            "Пожалуйста, выберите действие: 'Начать новый круг' или 'Завершить игру на сегодня'."
        )
        bot.register_next_step_handler(message, lambda message: handle_post_round_choice(bot, message))


def reset_tournament():
    """Сбрасывает всю статистику при новой регистрации игроков."""
    logging.info("Сбрасываем статистику турнира и все данные о матчах.")
    tournament.reset_statistics()
