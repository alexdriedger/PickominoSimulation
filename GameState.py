import math
import random
from collections import defaultdict
from Action import Action
from typing import DefaultDict, List


class GameState:

    MIN_DOMINO = 21
    MAX_DOMINO = 37

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
        self.player_turn = 0

        # saved_dice + dice_roll == num_dice
        self.num_dice = 8
        self.saved_dice = []
        self.dice_roll = []

        self.is_roll_resolved = True

    def __copy__(self):
        self.assert_valid_game_state()
        gs_copy = GameState(self.num_players)
        gs_copy.player_states = []
        for ps in self.player_states:
            gs_copy.player_states.append(ps.copy())
        gs_copy.community_dominoes = self.community_dominoes.copy()
        gs_copy.player_turn = self.player_turn
        gs_copy.saved_dice = self.saved_dice.copy()
        gs_copy.dice_roll = self.dice_roll.copy()
        gs_copy.assert_valid_game_state()
        return gs_copy

    def __str__(self):
        return f"num_players:{self.num_players}.player_states:{self.player_states}." \
            f"community_dominoes:{self.community_dominoes}.player_turn:{self.player_turn}." \
            f"num_dice:{self.num_dice}.saved_dice:{self.saved_dice}.dice_roll:{self.dice_roll}." \
            f"is_roll_resolved:{self.is_roll_resolved}"

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
            # print("Resolving dice roll")

            # Add die numbers that were rolled but have not been saved yet
            for die in set(self.dice_roll):
                if die not in self.saved_dice:
                    possible_actions.append(Action(Action.ACTION_SAVE_DICE, die))

        else:
            # Find the possible dominoes that can be taken
            # print("Checking if possible to take domino")

            # Must have a worm saved to take a domino
            if self.saved_dice.__contains__(6):
                score = 0
                for die in self.saved_dice:
                    if die == 6:
                        score += 5
                    else:
                        score += die

                # Check if community dominoes has the domino with current score
                # And if not, the next highest
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
            # print("Checking if possible to roll again")
            if len(set(self.saved_dice)) < 6 and len(self.saved_dice) < self.num_dice:
                possible_actions.append(Action(Action.ACTION_ROLL_DICE))

        if len(possible_actions) == 0:
            # Return only next player turn action
            # print("No possible actions for current player")
            possible_actions.append(Action(Action.ACTION_NEXT_PLAYER_TURN))

        return possible_actions

    def resolve_action(self, action: Action):
        """
        Play the action out on the state. Mutates game state. If you need a new state, first
        create a shallow copy of the state and then call resolve_action.
        :param action: Action to take
        """

        try:
            self.assert_valid_game_state()
        except AssertionError:
            self.print_current_state()
            print(action)
            raise

        if action.name == Action.ACTION_ROLL_DICE:
            # print("Rolling dice")
            self.dice_roll = [random.randrange(1, 7) for x in range(self.num_dice - len(self.saved_dice))]
            # print(f"Rolled:\t{self.dice_roll}")
            self.is_roll_resolved = False

            # Check if player busted
            if set(self.dice_roll).issubset(set(self.saved_dice)):
                # print("Player busted")
                self.lose_domino()
                self.increment_player_turn()
                # self.print_current_state()

        elif action.name == Action.ACTION_SAVE_DICE:
            # print("Saving dice")
            for die in self.dice_roll:
                if die == action.optional_args:
                    self.saved_dice.append(die)
            # print(f"Saved dice:\t{self.saved_dice}")
            self.dice_roll.clear()
            self.is_roll_resolved = True

        elif action.name == Action.ACTION_TAKE_DOMINO:
            # print(f"Taking domino:\t{action.optional_args}")
            prev_length = len(self.community_dominoes)
            # Remove domino from community dominoes
            self.community_dominoes[:] = [x for x in self.community_dominoes if not x == action.optional_args]

            # Domino was in a player stack
            if prev_length == len(self.community_dominoes):
                for player_num, player in enumerate(self.player_states):
                    if player_num != self.player_turn and len(player) > 0 and player[-1] == action.optional_args:
                        self.player_states[player_num] = player[:-1]
                        break

            # Add domino to player
            self.player_states[self.player_turn].append(action.optional_args)
            self.increment_player_turn()
            # print("Player states:")
            # for p in self.player_states:
            #     print(p)

        elif action.name == Action.ACTION_NEXT_PLAYER_TURN:
            self.lose_domino()
            self.increment_player_turn()

        # print("\n####### Completed Action ####")
        # print(f"Action:\t{action.name}\tArgs:\t{action.optional_args}")

        # Logging
        # if action.name == Action.ACTION_TAKE_DOMINO:
        #     print("\n####### Completed Action ####")
        #     print(f"Action:\t{action.name}\tArgs:\t{action.optional_args}")
        #     self.print_current_state()

        try:
            self.assert_valid_game_state()
        except AssertionError:
            # self.print_current_state()
            print(f"Action attempted:\t{action}")
            raise

    def lose_domino(self):
        # print("Losing domino")
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

    def increment_player_turn(self):
        # print("Next player's turn")
        # print("Resetting dice")
        self.saved_dice.clear()
        self.dice_roll.clear()
        self.is_roll_resolved = True
        if self.player_turn == self.num_players - 1:
            self.player_turn = 0
        else:
            self.player_turn += 1

    def print_current_state(self):
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
        sum = 0
        for i in self.player_states:
            sum += len(i)
        # print(f"sum: {sum}. community: {len(self.community_dominoes)}")
        # assert sum + len(self.community_dominoes) == self.MAX_DOMINO - self.MIN_DOMINO
        if sum + len(self.community_dominoes) > self.MAX_DOMINO - self.MIN_DOMINO:
            self.print_current_state()
            raise AssertionError("Invalid Game State")
