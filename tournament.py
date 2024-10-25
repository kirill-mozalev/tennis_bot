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
