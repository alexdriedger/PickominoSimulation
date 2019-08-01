from ai import *
from GameState import GameState


# TODO : Check ending logic, that the game ends at the correct time
# TODO : Make a slightly smarter AI to prefer to take dominoes more frequently
# TODO : Make AIs a function that can be passed in to take a player's turn
# TODO : Write some unit tests for GameState to make sure that it works correctly


def play_game(num_players):
    # Initialize a new game
    gs = GameState(num_players)

    # Assign an ai to each player
    player_ais = dict([
        (0, safe_ai),
        (1, safe_ai_better_die_saving),
        (2, safe_ai),
        (3, safe_ai_better_die_saving)
    ])

    # Every player plays a turn until the game is over
    while not gs.is_game_over():
        ai = player_ais.get(gs.player_turn)
        play_turn(gs, ai)

    print("Game Complete!")

    return gs


def play_turn(game_state: GameState, ai):
    current_player = game_state.player_turn

    while game_state.player_turn == current_player:
        chosen_action = ai(game_state, game_state.get_next_actions())
        # if chosen_action.name == Action.ACTION_TAKE_DOMINO:
            # game_state.print_current_state()
        game_state.resolve_action(chosen_action)


def simulate_games(num_games):
    num_players = 4
    finishes = dict()
    for player_num, x in enumerate(range(num_players)):
        finishes[player_num] = [0]*num_players
    for i in range(num_games):
        # Simulate game
        final_game_state = play_game(num_players)

        # Determine Placing
        worm_counts = final_game_state.calculate_worm_count()
        sorted_player_num_by_worm_count = sorted(worm_counts, key=worm_counts.get, reverse=True)
        for place, player in enumerate(sorted_player_num_by_worm_count):
            finishes[player][place] += 1

    # Log results
    for player_num, results in finishes.items():
        print(f"Player {player_num}:\t{results}")


simulate_games(200)
