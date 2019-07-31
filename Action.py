class Action:

    ACTION_ROLL_DICE = "Roll dice"
    ACTION_SAVE_DICE = "Save dice"
    ACTION_TAKE_DOMINO = "Take domino"
    ACTION_NEXT_PLAYER_TURN = "Next player turn"

    def __init__(self, name, optional_args=None):
        self.name = name
        self.optional_args = optional_args
