from random import choice
from collections import defaultdict
from GameState import GameState
from Action import Action


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


def random_ai(game_state: GameState, possible_actions: list):
    """
    Picks a random possible action
    :param game_state: GameState. Is not used by the random ai
    :param possible_actions: Possible actions to take
    :return: Random possible action
    """
    return choice(possible_actions)


def safe_ai(game_state: GameState, possible_actions: list):
    if len(possible_actions) == 1:
        return possible_actions[0]

    # Take a domino whenever possible
    take_domino_action = take_domino_if_possible(possible_actions)
    if take_domino_action is not None:
        return take_domino_action

    # Save the largest die available
    save_die_actions = [x for x in possible_actions if x.name == Action.ACTION_SAVE_DICE]
    if len(save_die_actions) > 0:
        return sorted(save_die_actions, key=lambda action: action.optional_args).pop()

    raise RuntimeError("Safe AI did not account for all possible action combinations")


def safe_ai_better_die_saving(game_state: GameState, possible_actions: list):
    if len(possible_actions) == 1:
        return possible_actions[0]

    # Take a domino whenever possible
    take_domino_action = take_domino_if_possible(possible_actions)
    if take_domino_action is not None:
        return take_domino_action

    # If >= 2 dice have been saved but no worms, save a worm if it's available
    set_saved_die = set(game_state.saved_dice)
    if len(set_saved_die) > 2 and not set_saved_die.__contains__(6) and set(game_state.dice_roll).__contains__(6):
        save_worm_action = [x for x in possible_actions if x.name == Action.ACTION_SAVE_DICE and x.optional_args == 6]
        assert len(save_worm_action) > 0
        return save_worm_action[0]

    # Save die with the largest total score
    counts = defaultdict(int)
    for die in game_state.dice_roll:
        if die == 6:
            counts[die] += 5
        else:
            counts[die] += die

    save_die_actions = [(x, x.optional_args, counts.get(x.optional_args)) for x in possible_actions if x.name == Action.ACTION_SAVE_DICE]
    sorted_actions = sorted(save_die_actions, key=lambda x: (x[2], x[1]))
    assert len(sorted_actions) > 0
    return sorted_actions.pop()[0]


def take_domino_if_possible(possible_actions):
    """
    Take a domino if possible. Takes the highest number domino available.
    :param possible_actions: Possible actions to take
    :return: Action to take if a domino is available. If no domino is available, returns None
    """
    take_domino_actions = [x for x in possible_actions if x.name == Action.ACTION_TAKE_DOMINO]
    if len(take_domino_actions) > 0:
        return sorted(take_domino_actions, key=lambda domino_action: domino_action.optional_args[0]).pop()
    return None


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
