import math
import random
from collections import defaultdict
from Action import Action
from typing import DefaultDict, List


class GameState:

    MIN_DOMINO = 21
    MAX_DOMINO = 37
    NUM_DICE = 8
    STARTING_PLAYER_TURN = 0
    DEBUG = True

    def __init__(self, num_players):
        """
        Create a GameState for a new game
        """
        self.num_players = num_players

        # Populate player states with an empty stack of dominoes
        self.player_states = []
        for i in range(0, num_players):
            self.player_states.append([])

        # Populate community dominoes
        self.community_dominoes = []
        for i in range(self.MIN_DOMINO, self.MAX_DOMINO):
            num_worms = math.floor((i - 17) / 4)
            self.community_dominoes.append((i, num_worms))

        # Turn for a player. Should be an int from [0-num_players)
        self.player_turn = self.STARTING_PLAYER_TURN

        # saved_dice + dice_roll == num_dice
        self.num_dice = self.NUM_DICE
        self.saved_dice = []
        self.dice_roll = []

        self.is_roll_resolved = True

    def __copy__(self):
        if self.DEBUG:
            self.assert_valid_game_state()
        gs_copy = GameState(self.num_players)
        gs_copy.player_states = []
        for ps in self.player_states:
            gs_copy.player_states.append(ps.copy())
        gs_copy.community_dominoes = self.community_dominoes.copy()
        gs_copy.player_turn = self.player_turn
        gs_copy.saved_dice = self.saved_dice.copy()
        gs_copy.dice_roll = self.dice_roll.copy()
        gs_copy.is_roll_resolved = self.is_roll_resolved
        if self.DEBUG:
            gs_copy.assert_valid_game_state()
        return gs_copy

    def __repr__(self):
        return f"num_players:{self.num_players}.player_states:{self.player_states}." \
            f"community_dominoes:{self.community_dominoes}.player_turn:{self.player_turn}." \
            f"num_dice:{self.num_dice}.saved_dice:{self.saved_dice}.dice_roll:{self.dice_roll}." \
            f"is_roll_resolved:{self.is_roll_resolved}"

    def __str__(self):
        return f"Player_turn:{self.player_turn}." \
            f"Saved_dice:{self.saved_dice}.Dice_roll:{self.dice_roll}.RR:{self.is_roll_resolved}." \
            f"Player_states:{self.player_states}." \
            f"Community_dominoes:{self.community_dominoes}."

    def is_game_over(self):
        if len(self.community_dominoes) == 0:
            return True
        return False

    def get_next_actions(self) -> List[Action]:
        """
        Get all possible actions to take based on the current game state. Does not mutate self
        :return: list of actions with >= 1 actions
        """

        possible_actions = []

        # Check if the game is over
        if self.is_game_over():
            print("Game over. Final game state below")
            self.print_current_state()
            raise RuntimeError("get_next_action shouldn't be called on a complete game")

        # Dice rolled. Need to select dice to keep
        if not self.is_roll_resolved:
            # Add die numbers that were rolled but have not been saved yet
            for die in set(self.dice_roll):
                if die not in self.saved_dice:
                    possible_actions.append(Action(Action.ACTION_SAVE_DICE, die))

        # Find the possible dominoes that can be taken
        else:
            # Must have a worm saved to take a domino
            if self.saved_dice.__contains__(6):
                score = 0
                for die in self.saved_dice:
                    if die == 6:
                        score += 5
                    else:
                        score += die

                # Check if community dominoes has the domino with current score
                # And if not, the next highest domino
                for domino in reversed(self.community_dominoes):
                    if domino[0] > score:
                        continue
                    elif domino[0] == score:
                        possible_actions.append(Action(Action.ACTION_TAKE_DOMINO, domino))
                        break
                    elif domino[0] < score:
                        possible_actions.append(Action(Action.ACTION_TAKE_DOMINO, domino))
                        break

                # Check if any player (excluding the current player) has the domino on the top
                # of their domino stack
                for player_num, player_dominoes in enumerate(self.player_states):
                    if player_num != self.player_turn and len(player_dominoes) > 0:
                        player_top_domino = player_dominoes[-1]
                        if player_top_domino[0] == score:
                            possible_actions.append(Action(Action.ACTION_TAKE_DOMINO, player_top_domino))

            # Check if possible to roll again
            if len(set(self.saved_dice)) < 6 and len(self.saved_dice) < self.num_dice:
                possible_actions.append(Action(Action.ACTION_ROLL_DICE))

        if len(possible_actions) == 0:
            # Return only next player turn action
            possible_actions.append(Action(Action.ACTION_NEXT_PLAYER_TURN))

        return possible_actions

    def resolve_action(self, action: Action):
        """
        Play the action out on the state. Mutates game state. If you need a new state, first
        create a shallow copy of the state and then call resolve_action.
        :param action: Action to take
        """

        # Ensure action is being resolved on a valid game state
        if self.DEBUG:
            try:
                self.assert_valid_game_state()
            except InvalidGameStateError:
                raise InvalidGameStateError("resolve_action called with invalid state", game_state=self, action=action)

        if action.name == Action.ACTION_ROLL_DICE:
            if self.DEBUG:
                # Check that rolling dice is a valid action
                if self.is_roll_resolved is False:
                    raise InvalidGameStateError("Attempted to roll dice when dice roll has not been resolved",
                                                game_state=self, action=action)
                if len(self.saved_dice) == self.NUM_DICE:
                    raise InvalidGameStateError("Attempted to roll dice when all dice have already been saved",
                                                game_state=self, action=action)
                if len(set(self.saved_dice)) == 6:
                    raise InvalidGameStateError("Attempted to roll dice when all dice all six dice numbers have been saved",
                                                game_state=self, action=action)

            # Roll dice
            self.dice_roll = [random.randrange(1, 7) for x in range(self.num_dice - len(self.saved_dice))]
            self.is_roll_resolved = False

            # Check if player busted
            if set(self.dice_roll).issubset(set(self.saved_dice)):
                self.lose_domino()
                self.increment_player_turn()

        elif action.name == Action.ACTION_SAVE_DICE:
            if self.DEBUG:
                # Check that rolling dice is a valid action
                if self.is_roll_resolved is True:
                    raise InvalidGameStateError("Attempted to save dice when roll has already been resolved",
                                                game_state=self, action=action)
                if action.optional_args in self.saved_dice:
                    raise InvalidGameStateError("Attempted to save dice number that was saved earlier in the player's turn",
                                                game_state=self, action=action)
                if action.optional_args not in self.dice_roll:
                    raise InvalidGameStateError("Attempted to save dice number that was not rolled", game_state=self,
                                                action=action)

            # Save all dice rolled of the number to be saved
            for die in self.dice_roll:
                if die == action.optional_args:
                    self.saved_dice.append(die)
            self.dice_roll.clear()
            self.is_roll_resolved = True

        elif action.name == Action.ACTION_TAKE_DOMINO:
            prev_length = len(self.community_dominoes)

            # Remove domino from community dominoes
            self.community_dominoes[:] = [x for x in self.community_dominoes if not x == action.optional_args]

            # Domino was in a player stack
            if prev_length == len(self.community_dominoes):
                domino_found = False
                for player_num, player in enumerate(self.player_states):
                    if player_num != self.player_turn and len(player) > 0 and player[-1] == action.optional_args:
                        self.player_states[player_num] = player[:-1]
                        domino_found = True
                        break
                if domino_found is False:
                    raise InvalidGameStateError("Attempted to take a domino that was not available", game_state=self,
                                                action=action)

            # Add domino to player
            self.player_states[self.player_turn].append(action.optional_args)
            self.increment_player_turn()

        elif action.name == Action.ACTION_NEXT_PLAYER_TURN:
            self.lose_domino()
            self.increment_player_turn()

        if self.DEBUG:
            # Ensure GameState is still valid after completing action
            try:
                self.assert_valid_game_state()
            except InvalidGameStateError:
                raise InvalidGameStateError("GameState after resolving action is invalid", game_state=self, action=action)

    def lose_domino(self) -> bool:
        """
        The current player loses the domino on the top of their stack if they have any dominoes. If a player loses a
        domino, that domino is added back to the community dominoes and the largest community domino is removed from
        the game.
        :return: True if player lost a domino
        """
        # Only lose domino if player has 1 or more dominoes
        if len(self.player_states[self.player_turn]) > 0:
            domino = self.player_states[self.player_turn][-1]

            # Remove domino from player
            self.player_states[self.player_turn] = self.player_states[self.player_turn][:-1]

            # Add domino back to community in sorted order
            num_community_dominoes = len(self.community_dominoes)
            for index, community_domino in enumerate(self.community_dominoes):
                if domino < community_domino:
                    self.community_dominoes[index:index] = [domino]
                    break
                if index == num_community_dominoes - 1:
                    self.community_dominoes.append(domino)

            # Remove largest community domino from the game
            self.community_dominoes = self.community_dominoes[:-1]
            return True
        return False

    def increment_player_turn(self) -> None:
        """
        Increments the player turn and resets dice state
        :return: None
        """
        # Reset Dice
        self.saved_dice.clear()
        self.dice_roll.clear()
        self.is_roll_resolved = True

        # Increment player turn
        if self.player_turn == self.num_players - 1:
            self.player_turn = 0
        else:
            self.player_turn += 1

    def print_current_state(self) -> None:
        """
        Prints current game state. Useful for debugging.
        """
        score = 0
        for die in self.saved_dice:
            if die == 6:
                score += 5
            else:
                score += die

        print("####### Current State #######\n")

        print(f"Roll Resolved:\t{self.is_roll_resolved}")
        print(f"Saved Dice:\t\t{self.saved_dice}\tScore:\t{score}")
        print(f"Rolled Dice:\t{self.dice_roll}\n")

        print(f"Community Dominoes:")
        print(self.community_dominoes)
        for player_num, dominoes in enumerate(self.player_states):
            score = 0
            for d in dominoes:
                score += d[1]
            if player_num == self.player_turn:
                print("*", end='')
            print(f"Player {player_num}:\t{dominoes}\tWorms:\t{score}")
        print("#############################\n")

    def calculate_worm_count(self) -> DefaultDict[int, int]:
        """
        Returns the number of worms each player has
        :return: Dictionary mapping player number to number of worms that player has
        """
        counts = defaultdict(int)
        for player_num, dominoes in enumerate(self.player_states):
            for d in dominoes:
                counts[player_num] += d[1]
            if len(dominoes) == 0:
                counts[player_num] = 0
        return counts

    def assert_valid_game_state(self):
        # Check that there is not more than the starting number of dominoes present in the game
        total_game_dominoes = 0
        for i in self.player_states:
            total_game_dominoes += len(i)
        if total_game_dominoes + len(self.community_dominoes) > self.MAX_DOMINO - self.MIN_DOMINO:
            self.print_current_state()
            raise InvalidGameStateError("Invalid number of dominoes in the game", game_state=self)

        # Check that extra dice did not appear
        if len(self.saved_dice) + len(self.dice_roll) > self.NUM_DICE:
            raise InvalidGameStateError("Invalid number of dice (saved + rolled)", game_state=self)


class InvalidGameStateError(RuntimeError):
    """
    Error to be used when the GameState has an internal inconsistency or an action is trying to change the state in a
    way that is invalid
    """
    def __init__(self, msg, game_state: GameState, action=None):
        game_state.print_current_state()
        if action is not None:
            print(f"Action that caused an invalid GameState:\t{action}")
        super()
