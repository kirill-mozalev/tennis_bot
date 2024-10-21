from itertools import combinations
import random

def get_match_schedule(players):
    """
    Генерирует полную сетку матчей по круговому принципу, чтобы каждый игрок сыграл с каждым.
    """
    # Генерируем все возможные пары игроков
    all_matches = list(combinations(players, 2))

    # Перемешиваем пары случайным образом для разнообразия
    random.shuffle(all_matches)

    final_schedule = []
    last_players = set()

    # Проходим по всем матчам и балансируем расписание
    while all_matches:
        for match in all_matches[:]:
            player1, player2 = match

            # Проверяем, чтобы игроки не играли подряд
            if player1 not in last_players and player2 not in last_players:
                final_schedule.append(match)
                last_players = {player1, player2}  # Обновляем последние сыгравшие пары
                all_matches.remove(match)
                break
        else:
            # Если не удалось найти подходящую пару (все игроки играли недавно), сбрасываем последних игроков
            last_players.clear()

    return final_schedule
