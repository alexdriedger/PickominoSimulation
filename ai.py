from random import choice
from collections import defaultdict
from math import sqrt
from typing import List
from timeit import default_timer as timer
from GameState import GameState
from Action import Action


def random_ai(game_state: GameState, possible_actions: List[Action]) -> Action:
    """
    Picks a random possible action
    :param game_state: GameState. Is not used by the random ai
    :param possible_actions: Possible actions to take
    :return: Random possible action
    """
    return choice(possible_actions)


def safe_ai(game_state: GameState, possible_actions: List[Action]) -> Action:
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


def safe_ai_better_die_saving(game_state: GameState, possible_actions: List[Action]) -> Action:
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


def take_domino_if_possible(possible_actions: List[Action]):
    """
    Take a domino if possible. Takes the highest number domino available.
    :param possible_actions: Possible actions to take
    :return: Action to take if a domino is available. If no domino is available, returns None
    """
    take_domino_actions = [x for x in possible_actions if x.name == Action.ACTION_TAKE_DOMINO]
    if len(take_domino_actions) > 0:
        return sorted(take_domino_actions, key=lambda domino_action: domino_action.optional_args[0]).pop()
    return None


def monte_carlo_ai_random_playouts(game_state: GameState, possible_actions: List[Action]) -> Action:
    """
    Uses a Monte Carlo Tree Search with random playouts at the simulation step to determine
    the best next move

    :param game_state: Current GameState
    :param possible_actions: Possible actions to take
    :return: Next action to take
    """
    if len(possible_actions) == 1:
        return possible_actions[0]

    NUM_SIMS = 200

    Qsa = {}
    Nsa = {}
    Ns = {}
    visited = set()

    # Simulate playouts
    for num_playout in range(NUM_SIMS):
        mcts_search(game_state, game_state.player_turn, game_state.calculate_worm_count().get(game_state.player_turn),
                    Qsa, Nsa, Ns, visited)
    s = str(game_state)

    sorted_actions = sorted(possible_actions, key=lambda a: Nsa.get((s, str(a)), float("-inf")))
    # game_state.print_current_state()
    # print([str(x) for x in sorted_actions])
    # nums = []
    # for a in possible_actions:
    #     nums.append((str(a), Nsa.get((s, str(a)))))
    # print(nums)
    return sorted_actions.pop()


def mcts_search(game_state: GameState, player_turn, num_worms, Qsa, Nsa, Ns, visited):
    if game_state.player_turn != player_turn:
        return get_change_worm_count(game_state, player_turn, num_worms)

    s = str(game_state)
    if s not in visited:
        visited.add(s)
        Ns[s] = 0
        gs_copy = game_state.__copy__()
        gs_end_turn = random_rollout_result(gs_copy, player_turn)
        game_state.assert_valid_game_state()
        return get_change_worm_count(gs_end_turn, player_turn, num_worms)

    ucb_action = get_best_action_ucb(game_state, Qsa, Nsa, Ns)
    next_state = game_state.__copy__()
    next_state.resolve_action(ucb_action)
    v = mcts_search(next_state, player_turn, num_worms, Qsa, Nsa, Ns, visited)
    update_search_values(v, s, str(ucb_action), Qsa, Nsa, Ns)
    return v


def get_change_worm_count(game_state: GameState, player: int, orig_num_worms: int) -> int:
    """
    Returns the difference between the original worm count and the worm count in the current
    game state for a given player
    :param game_state: Game state to get current worm counts from
    :param player: Player number to calculate change in worm count for
    :param orig_num_worms: Original worm count to calculate against
    :return: Difference in worm count for player between the current worm count in game_state and orig_num_worms
    """
    worm_counts = game_state.calculate_worm_count()
    return worm_counts[player] - orig_num_worms


def random_rollout_result(game_state: GameState, player_turn: int):
    """
    Performs a random rollout from a given game state for the current player until the end of their turn
    :param game_state: GameState to perform rollout from
    :param player_turn: Player to perform rollout for. Rollout finishes when this player's turn is over
    :return: GameState after the player's turn is over
    """
    while game_state.player_turn == player_turn:
        possible_actions = game_state.get_next_actions()
        game_state.resolve_action(choice(possible_actions))

    return game_state


def get_best_action_ucb(game_state: GameState, Qsa, Nsa, Ns) -> Action:
    """
    Get the best valid action, calculate by Upper Confidence Bound.
    :param game_state: Current GameState
    :param Qsa: Dictionary of Q values for state, action tuples
    :param Nsa: Dictionary of counts of times a state, action tuple has been taken
    :param Ns: Dictionary of counts of times a state has been taken
    :return: Best valid action
    """
    c = 1.41
    s = str(game_state)
    possible_actions = game_state.get_next_actions()

    # Calculate best action using UCB
    best_u = -float("inf")
    best_a = None
    for action in possible_actions:
        a = str(action)
        if (s, a) in Qsa:
            u = Qsa[(s, a)] + c * sqrt(Ns[s])/(1 + Nsa[(s, a)])
        else:
            u = c * sqrt(Ns[s] + 0.0000001)

        if u > best_u:
            best_u = u
            best_a = action

    return best_a


def update_search_values(v: int, s: str, a: str, Qsa, Nsa, Ns):
    if (s, a) in Qsa:
        Qsa[(s, a)] = (Nsa[(s, a)] * Qsa[(s, a)] + v) / (Nsa[(s, a)] + 1)
        Nsa[(s, a)] += 1
    else:
        Qsa[(s, a)] = v
        Nsa[(s, a)] = 1

    Ns[s] += 1
