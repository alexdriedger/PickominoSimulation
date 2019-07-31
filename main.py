from random import choice
from GameState import GameState


def play_turn(state):
    """
    Play a turn of a given state until the end of the player's turn
    :param state: game state
    :return: nothing
    """


gs = GameState(4)

count = 0
while count < 20 and len(gs.community_dominoes) > 0:
    possible_actions = gs.get_next_actions()
    print([(x.name, x.optional_args) for x in possible_actions])
    gs.resolve_action(choice(possible_actions))
    count += 1


