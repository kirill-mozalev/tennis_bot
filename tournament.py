class Tournament:
    def __init__(self):
        self.players = []
        self.matches = []
        self.current_match_index = 0
        self.total_results = {}   # Общая статистика за все круги
        self.round_results = {}   # Статистика текущего круга

    def add_player(self, player):
        self.players.append(player)

    def set_matches(self, matches):
        self.matches = matches
        self.current_match_index = 0
        self.round_results = {player: 0 for player in self.players}  # Сброс статистики текущего круга

    def get_current_match(self):
        if self.current_match_index < len(self.matches):
            return self.matches[self.current_match_index]
        return None

    def increment_match_index(self):
        self.current_match_index += 1

    def add_win(self, winner):
        # Обновляем статистику текущего круга
        if winner in self.round_results:
            self.round_results[winner] += 1
        else:
            self.round_results[winner] = 1
        # Обновляем общую статистику
        if winner in self.total_results:
            self.total_results[winner] += 1
        else:
            self.total_results[winner] = 1

    def get_round_results(self):
        return self.round_results

    def get_total_results(self):
        return self.total_results

    def is_tournament_finished(self):
        return self.current_match_index >= len(self.matches)

    def reset_statistics(self):
        """Сбрасываем всю статистику, если нужно начать с нуля."""
        self.total_results = {}
        self.round_results = {}
        self.current_match_index = 0
        self.matches = []
