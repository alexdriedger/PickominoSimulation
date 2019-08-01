from random import choice
from collections import defaultdict
from GameState import GameState
from Action import Action

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
