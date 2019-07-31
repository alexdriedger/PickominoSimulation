from random import choice
from GameState import GameState


# TODO : Check ending logic, that the game ends at the correct time
# TODO : Make a slightly smarter AI to prefer to take dominoes more frequently
gs = GameState(4)

count = 0
while count < 500 and len(gs.community_dominoes) > 0:
    possible_actions = gs.get_next_actions()
    # print([(x.name, x.optional_args) for x in possible_actions])
    gs.resolve_action(choice(possible_actions))
    count += 1


