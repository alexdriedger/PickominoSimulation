import unittest
from GameState import GameState
from Action import Action


class TakingDominoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.game_state = GameState(4)
        self.game_state.community_dominoes.remove((22, 1))
        self.game_state.community_dominoes.remove((25, 2))
        self.game_state.community_dominoes.remove((30, 3))
        self.game_state.player_states = [[], [(22, 1), (30, 3)], [(25, 2)], []]

    def test_steal_domino(self):
        action = Action(Action.ACTION_TAKE_DOMINO, (30, 3))
        self.game_state.resolve_action(action)
        self.assertListEqual(self.game_state.player_states, [[(30, 3)], [(22, 1)], [(25, 2)], []])

    def test_steal_from_bottom_of_stack(self):
        self.game_state.saved_dice = [6, 6, 5, 5, 2]
        self.game_state.is_roll_resolved = True
        potential_actions = self.game_state.get_next_actions()
        self.assertEqual(len(potential_actions), 2)
        self.assertIn(Action(Action.ACTION_ROLL_DICE), potential_actions)
        self.assertIn(Action(Action.ACTION_TAKE_DOMINO, (21, 1)), potential_actions)

    def test_steal_domino_from_self(self):
        self.game_state.community_dominoes.remove((23, 1))
        self.game_state.player_states = [[(23, 1)], [(22, 1), (30, 3)], [(25, 2)], []]
        self.game_state.saved_dice = [6, 6, 5, 5, 3]
        self.game_state.is_roll_resolved = True
        potential_actions = self.game_state.get_next_actions()
        self.assertEqual(len(potential_actions), 2)
        self.assertIn(Action(Action.ACTION_ROLL_DICE), potential_actions)
        self.assertIn(Action(Action.ACTION_TAKE_DOMINO, (21, 1)), potential_actions)

    def test_steal_smallest_domino_from_self(self):
        self.game_state.community_dominoes.remove((21, 1))
        self.game_state.player_states = [[(21, 1)], [(22, 1), (30, 3)], [(25, 2)], []]
        self.game_state.saved_dice = [6, 6, 5, 5, 1]
        self.game_state.is_roll_resolved = True
        potential_actions = self.game_state.get_next_actions()
        self.assertEqual(len(potential_actions), 1)
        self.assertIn(Action(Action.ACTION_ROLL_DICE), potential_actions)


if __name__ == '__main__':
    unittest.main()