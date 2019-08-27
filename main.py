from ai import *
from GameState import GameState
import matplotlib.pyplot as plt
import numpy


def play_game(num_players: int, player_ais) -> GameState:
    """
    Play a game until the game finishes. The player ai for each position chooses moves to play
    on its turn
    :param num_players: Number of players in the game
    :param player_ais: Dictionary mapping player number to ai function
    :return: Final GameState
    """
    # Initialize a new game
    gs = GameState(num_players)

    # Every player plays a turn until the game is over
    while not gs.is_game_over():
        ai = player_ais.get(gs.player_turn)
        play_turn(gs, ai)

    return gs


def play_turn(game_state: GameState, ai) -> None:
    """
    Play a single turn in a game using the ai to select moves to take.
    :param game_state: GameState at the start of the turn
    :param ai: Function to choose the next action, based on the current GameState
    :return: None
    """
    current_player = game_state.player_turn

    while game_state.player_turn == current_player:
        game_state.assert_valid_game_state()
        chosen_action = ai(game_state, game_state.get_next_actions())
        game_state.resolve_action(chosen_action)


def simulate_games(num_games):
    num_players = 4
    # Assign an ai to each player
    player_ais = dict([
        (0, monte_carlo_ai_random_playouts),
        (1, safe_ai_better_die_saving),
        (2, monte_carlo_ai_random_playouts),
        (3, safe_ai_better_die_saving)
    ])

    player_ais_no_monte_carlo = dict([
        (0, safe_ai),
        (1, safe_ai_better_die_saving),
        (2, random_ai),
        (3, safe_ai_better_die_saving)
    ])

    # Simulate games
    game_results = []
    for i in range(num_games):
        game_results.append(play_game(num_players, player_ais_no_monte_carlo))
        print(f"Finished game {i}")

    domino_counts = dict()
    for i in range(num_players):
        domino_counts[i] = []
    print(domino_counts)
    # Analyze results
    for g_num, game in enumerate(game_results):
        # Counts for each game
        # domino_counts = numpy.zeros((len(game_results), num_players))
        # domino_counts[g_num] = [count for player, count in game.calculate_worm_count().items()]

        c = game.calculate_worm_count()
        print(c)
        for player_num, wc in c.items():
            domino_counts[player_num].append(wc)

    print(domino_counts)
    fig, ax = plt.subplots()
    colors = {
        0: "bs-",
        1: "g^-",
        2: "cv-",
        3: "mh-"
    }
    for player_num in range(num_players):
        dc = numpy.array(domino_counts[player_num])
        unique, counts = numpy.unique(dc, return_counts=True)
        c = dict(zip(unique, counts))
        x = []
        y = []
        # Add 0 in for all numbers of worms that were not ended the game with
        for _ in range(21):
            if _ not in c:
                x.append(_)
                y.append(0)
            else:
                x.append(_)
                y.append(c[_])

        print(c)

        ax.set_autoscaley_on(False)
        ax.set_ylim([0, num_games])
        ax.set_autoscalex_on(False)
        ax.set_xlim([0, 20])
        plt.plot(x, y, colors[player_num])
    plt.show()


    # # Determine Placing
    # worm_counts = final_game_state.calculate_worm_count()
    # sorted_player_num_by_worm_count = sorted(worm_counts, key=worm_counts.get, reverse=True)
    # prev_place = 0
    # for place, player in enumerate(sorted_player_num_by_worm_count):
    #     if place != 0 and worm_counts.get(sorted_player_num_by_worm_count[place - 1]) == worm_counts.get(
    #             sorted_player_num_by_worm_count[place]):
    #         finishes[player][prev_place] += 1
    #     else:
    #         prev_place = place
    #         finishes[player][prev_place] += 1


simulate_games(5000)
