import logging
from telebot import types
from collections import defaultdict

class Tournament:
    def __init__(self):
        self.matches = []
        self.current_match_index = 0
        self.current_round_wins = defaultdict(int)  # Победы текущего круга
        self.total_wins = defaultdict(int)          # Общие победы за все круги

    def set_matches(self, matches):
        self.matches = matches
        self.current_match_index = 0

    def get_current_match(self):
        if self.current_match_index < len(self.matches):
            return self.matches[self.current_match_index]
        return None

    def increment_match_index(self):
        self.current_match_index += 1

    def add_result(self, winner):
        # Обновляем победы для текущего круга
        self.current_round_wins[winner] += 1
        logging.info(f"Победа добавлена игроку {winner} в текущем круге. Текущие победы: {self.current_round_wins}")

    def is_round_finished(self):
        return self.current_match_index >= len(self.matches)

    def end_round(self):
        # По окончании круга добавляем победы текущего круга в общую статистику
        for player, wins in self.current_round_wins.items():
            self.total_wins[player] += wins
        self.current_round_wins.clear()  # Очищаем статистику текущего круга
        self.current_match_index = 0     # Сбрасываем индекс матчей для следующего круга
        logging.info(f"Раунд завершен. Общая статистика побед: {self.total_wins}")

    def get_round_statistics(self):
        # Возвращает статистику текущего круга
        return dict(self.current_round_wins)

    def get_total_statistics(self):
        # Возвращает общую статистику за все круги
        return dict(self.total_wins)


# Инициализация турнира как глобальной переменной
tournament = Tournament()


def start_game(bot, chat_id, matches):
    global tournament  # Используем глобальный турнир
    tournament.set_matches(matches)  # Устанавливаем матчи для турнира

    if tournament.get_current_match():
        show_current_match(bot, chat_id, tournament)
    else:
        bot.send_message(chat_id, "Нет матчей для начала игры.")


def show_current_match(bot, chat_id, tournament):
    match = tournament.get_current_match()
    if not match:
        bot.send_message(chat_id, "Все матчи завершены!")
        logging.info(f"Все матчи завершены для чата {chat_id}.")
        end_round(bot, chat_id, tournament)  # Завершаем текущий круг
        return

    match_number, player1, player2 = match

    logging.info(f"Показываем матч {match_number}: {player1} vs {player2} для чата {chat_id}.")

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button1 = types.KeyboardButton(f"{player1} победил")
    button2 = types.KeyboardButton(f"{player2} победил")
    markup.add(button1, button2)

    bot.send_message(chat_id, f"Текущий матч: {player1} vs {player2}\nВыберите победителя:", reply_markup=markup)

    # Запрашиваем результат матча и передаем объект турнира
    bot.register_next_step_handler_by_chat_id(chat_id, lambda msg: handle_match_result(bot, msg, tournament))


def handle_match_result(bot, message, tournament):
    winner = message.text.replace(" победил", "")
    tournament.add_result(winner)  # Добавляем результат
    logging.info(f"Победитель выбран: {winner}")

    bot.send_message(message.chat.id, f"Победитель: {winner}")

    # Переходим к следующему матчу
    tournament.increment_match_index()

    if tournament.is_round_finished():
        end_round(bot, message.chat.id, tournament)
        return

    show_current_match(bot, message.chat.id, tournament)


def end_round(bot, chat_id, tournament):
    # Завершаем текущий круг и обновляем общую статистику
    tournament.end_round()

    # Статистика текущего круга
    current_round_stats = tournament.get_round_statistics()
    current_round_message = "Статистика текущего круга:\n" + "\n".join([f"{player}: {wins} побед" for player, wins in current_round_stats.items()])

    # Общая статистика за все круги
    total_stats = tournament.get_total_statistics()
    total_stats_message = "Общая статистика побед за все круги:\n" + "\n".join([f"{player}: {wins} побед" for player, wins in total_stats.items()])

    # Отправляем статистику в чат
    bot.send_message(chat_id, current_round_message)
    bot.send_message(chat_id, total_stats_message)

    # Кнопки для нового круга или завершения игры
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Начать новый круг', 'Завершить игру на сегодня')
    bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(chat_id, lambda msg: handle_round_action(bot, msg, tournament))


def handle_round_action(bot, message, tournament):
    if message.text == 'Начать новый круг':
        # Начинаем новый круг с теми же матчами
        start_game(bot, message.chat.id, tournament.matches)
    elif message.text == 'Завершить игру на сегодня':
        bot.send_message(message.chat.id, "Игра завершена! Спасибо за участие.")
