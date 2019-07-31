import math
import random
from Action import Action


class GameState:

    # # Determine best way to pass optional param with save dice and take domino action
    # ACTION_ROLL_DICE = "Roll dice"
    # ACTION_SAVE_DICE = "Save dice"
    # ACTION_TAKE_DOMINO = "Take domino"
    # ACTION_NEXT_PLAYER_TURN = "Next player turn"

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
        for i in range(21, 37):
            num_worms = math.floor((i - 17) / 4)
            self.community_dominoes.append((i, num_worms))

        # Turn for a player. Should be an int from [0-num_players)
        self.player_turn = 0

        # saved_dice + dice_roll == num_dice
        self.num_dice = 8
        self.saved_dice = []
        self.dice_roll = []

        self.is_roll_resolved = True

    # def __copy__(self):

    def get_next_actions(self):
        """
        Get all possible actions to take based on the current game state. Does not mutate self
        :return: list of actions with >= 1 actions
        """

        possible_actions = []

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
                        if player_dominoes[len(player_dominoes) - 1][0] == score:
                            possible_actions.append(Action(Action.ACTION_TAKE_DOMINO, domino))

            # Check if possible to roll again
            # print("Checking if possible to roll again")
            if len(set(self.saved_dice)) < 6 and len(self.saved_dice) < self.num_dice:
                possible_actions.append(Action(Action.ACTION_ROLL_DICE))

        if len(possible_actions) == 0:
            # Return only next player turn action
            # print("No possible actions for current player")
            possible_actions.append(Action(Action.ACTION_NEXT_PLAYER_TURN))

        return possible_actions

    def resolve_action(self, action):
        """
        Play the action out on the state. Mutates game state
        :param action: action to take
        :return: state after action completed
        """

        # global ACTION_ROLL_DICE
        # global ACTION_SAVE_DICE
        # global ACTION_TAKE_DOMINO
        # global ACTION_NEXT_PLAYER_TURN

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
            print(f"Taking domino:\t{action.optional_args}")
            prev_length = len(self.community_dominoes)
            # Remove domino from community dominoes
            self.community_dominoes[:] = [x for x in self.community_dominoes if not x == action.optional_args]

            # Domino was in a player stack
            if prev_length == len(self.community_dominoes):
                for player_num, player in enumerate(self.player_states):
                    if player_num != self.player_turn and player[-1] == action.optional_args:
                        self.player_states[self.player_turn] = player[:-1]
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
        if action.name == Action.ACTION_TAKE_DOMINO:
            print("\n####### Completed Action ####")
            print(f"Action:\t{action.name}\tArgs:\t{action.optional_args}")
            self.print_current_state()

    def lose_domino(self):
        print("Losing domino")
        if len(self.player_states[self.player_turn]) > 0:
            domino = self.player_states[self.player_turn][-1]
            # Remove domino from player
            self.player_states[self.player_turn] = self.player_states[self.player_turn][:-1]
            # Add domino back to community
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