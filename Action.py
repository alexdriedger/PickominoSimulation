class Action:

    ACTION_ROLL_DICE = "Roll dice"
    ACTION_SAVE_DICE = "Save dice"
    ACTION_TAKE_DOMINO = "Take domino"
    ACTION_NEXT_PLAYER_TURN = "Next player turn"

    def __init__(self, name, optional_args=None):
        self.name = name
        self.optional_args = optional_args

    def __str__(self):
        return f"({self.name}, {str(self.optional_args)})"

    def __eq__(self, other):
        return self.name == other.name and self.optional_args == other.optional_args
