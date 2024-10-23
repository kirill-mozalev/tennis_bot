import logging
from telebot import types
from collections import defaultdict


class Tournament:
    def __init__(self):
        self.current_match_index = 0
        self.matches = []
        self.results = []
        self.victories = defaultdict(int)  # Словарь для подсчета побед игроков за текущий круг
        self.total_victories = defaultdict(int)  # Словарь для общего подсчета побед игроков

    def set_matches(self, matches):
        self.matches = matches

    def get_current_match(self):
        if self.current_match_index < len(self.matches):
            return self.matches[self.current_match_index]
        return None

    def increment_match_index(self):
        self.current_match_index += 1

    def add_result(self, winner):
        self.results.append(winner)  # Добавляем результат текущего круга
        self.victories[winner] += 1  # Увеличиваем счетчик побед для победителя текущего круга
        self.total_victories[winner] += 1  # Увеличиваем общий счетчик побед для победителя

    def is_tournament_finished(self):
        return self.current_match_index >= len(self.matches)

    def get_results(self):
        return self.results

    def get_victories(self):
        return dict(self.victories)  # Возвращаем словарь победителей текущего круга

    def get_total_victories(self):
        return dict(self.total_victories)  # Возвращаем словарь общего количества побед


def start_game(bot, chat_id, matches):
    tournament = Tournament()  # Создаем новый турнир
    tournament.set_matches(matches)  # Устанавливаем матчи турнира

    if tournament.get_current_match():
        show_current_match(bot, chat_id, tournament)
    else:
        bot.send_message(chat_id, "Нет матчей для начала игры.")


def show_current_match(bot, chat_id, tournament):
    match = tournament.get_current_match()
    if not match:
        bot.send_message(chat_id, "Все матчи завершены!")
        logging.info(f"Все матчи завершены для чата {chat_id}.")
        end_tournament(bot, chat_id, tournament)
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

    if tournament.is_tournament_finished():
        bot.send_message(message.chat.id, "Турнир завершён! Вот результаты текущего круга:")
        results = tournament.get_results()
        results_message = "\n".join(results)
        bot.send_message(message.chat.id, results_message)
        end_tournament(bot, message.chat.id, tournament)
        return

    show_current_match(bot, message.chat.id, tournament)


def end_tournament(bot, chat_id, tournament):
    # Общая статистика побед
    total_victories = tournament.get_total_victories()
    victory_message = "Статистика побед за все круги:\n" + "\n".join(
        [f"{player}: {count} побед" for player, count in total_victories.items()])

    # Создаем кнопки для нового круга или завершения игры
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Начать новый круг', 'Завершить игру на сегодня')

    bot.send_message(chat_id, victory_message, reply_markup=markup)

    # Регистрация обработчика для кнопки "Начать новый круг"
    @bot.message_handler(func=lambda message: message.text == 'Начать новый круг')
    def start_new_round(message):
        bot.send_message(chat_id, "Запускаем новый круг матчей.")
        tournament.current_match_index = 0  # Сбрасываем индекс матчей для нового круга
        tournament.victories.clear()  # Очищаем статистику побед текущего круга
        start_game(bot, chat_id, tournament.matches)  # Перезапуск игры с теми же матчами

    # Регистрация обработчика для кнопки "Завершить игру на сегодня"
    @bot.message_handler(func=lambda message: message.text == 'Завершить игру на сегодня')
    def finish_game(message):
        bot.send_message(chat_id, "Спасибо за игру! До новых встреч!")
