import unittest
from GameState import GameState
from Action import Action


class GameStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.game_state = GameState(4)

    def test_take_first_domino(self):
        action = Action(Action.ACTION_TAKE_DOMINO, self.game_state.community_dominoes[0])
        self.game_state.resolve_action(action)
        self.assertEqual(len(self.game_state.player_states[0]), 1)
        self.assertListEqual(self.game_state.player_states[0], [(21, 1)])
        self.assertEqual(len(self.game_state.community_dominoes), 15)

    def test_save_dice(self):
        self.game_state.dice_roll = [3, 3, 4, 2, 3, 5, 5, 6]
        self.game_state.is_roll_resolved = False
        action = Action(Action.ACTION_SAVE_DICE, 5)
        self.game_state.resolve_action(action)
        self.assertListEqual(self.game_state.saved_dice, [5, 5])

    def test_copy(self):
        self.game_state.player_turn = 1
        gs_copy = self.game_state.__copy__()

        self.assertEqual(gs_copy.num_players, self.game_state.num_players)

        for player_num, gs_copy_player_dominoes in enumerate(gs_copy.player_states):
            self.assertListEqual(gs_copy_player_dominoes, self.game_state.player_states[player_num])

        self.assertListEqual(gs_copy.community_dominoes, self.game_state.community_dominoes)

        self.assertEqual(gs_copy.player_turn, self.game_state.player_turn)
        self.assertEqual(gs_copy.num_dice, self.game_state.num_dice)
        self.assertListEqual(gs_copy.saved_dice, self.game_state.saved_dice)
        self.assertListEqual(gs_copy.dice_roll, self.game_state.dice_roll)
        self.assertEqual(gs_copy.is_roll_resolved, self.game_state.is_roll_resolved)

    def test_copy_take_domino(self):
        starting_dominoes = [(21, 1), (23, 1), (24, 1), (26, 2), (27, 2), (28, 2), (29, 3), (31, 3),
                             (32, 3), (33, 4), (34, 4), (35, 4), (36, 4)]
        starting_player_states = [[], [(22, 1), (30, 3)], [(25, 2)], []]
        self.game_state.community_dominoes = [(21, 1), (23, 1), (24, 1), (26, 2), (27, 2), (28, 2), (29, 3), (31, 3),
                                              (32, 3), (33, 4), (34, 4), (35, 4), (36, 4)]
        self.game_state.player_states = [[], [(22, 1), (30, 3)], [(25, 2)], []]

        gs_copy = self.game_state.__copy__()
        action = Action(Action.ACTION_TAKE_DOMINO, (30, 3))
        gs_copy.resolve_action(action)
        self.assertListEqual(gs_copy.player_states, [[(30, 3)], [(22, 1)], [(25, 2)], []])

        self.assertListEqual(self.game_state.community_dominoes, starting_dominoes)
        self.assertListEqual(self.game_state.player_states, starting_player_states)

    def test_action_strings(self):
        self.game_state.dice_roll = [3, 4, 3, 5, 4, 2, 1, 1]
        self.game_state.is_roll_resolved = False
        pa1 = self.game_state.get_next_actions()
        pa2 = self.game_state.get_next_actions()
        self.assertListEqual(pa1, pa2)
        self.assertListEqual([str(x) for x in pa1], [str(x) for x in pa2])

    def test_action_strings_with_dominoes(self):
        self.game_state.saved_dice = [1, 2, 3, 4, 5, 6, 6, 6]
        self.game_state.is_roll_resolved = True
        pa = self.game_state.get_next_actions()
        self.assertEqual(len(pa), 1)
        self.assertEqual(pa[0], Action(Action.ACTION_TAKE_DOMINO, (30, 3)))
        self.assertEqual(str(pa[0]), str(Action(Action.ACTION_TAKE_DOMINO, (30, 3))))


if __name__ == '__main__':
    unittest.main()