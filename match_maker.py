from itertools import combinations
import random

def get_match_schedule(players):
    """Генерирует полную сетку матчей по круговому принципу, чтобы каждый игрок сыграл с каждым."""
    all_matches = list(combinations(players, 2))
    random.shuffle(all_matches)

    final_schedule = []
    last_players = set()

    while all_matches:
        for match in all_matches[:]:
            player1, player2 = match
            if player1 not in last_players and player2 not in last_players:
                final_schedule.append(match)
                last_players = {player1, player2}
                all_matches.remove(match)
                break
        else:
            last_players.clear()

    return final_schedule
