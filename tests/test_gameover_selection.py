import unittest
from unittest.mock import patch
from codes.gameover import GameOverRules


class SelectionTests(unittest.TestCase):
    def test_new_play_draws_only_one_of_first_two_rules(self):
        with patch('codes.gameover.random.choice', side_effect=AssertionError('무작위 추첨 금지')) as choose:
            self.assertEqual(GameOverRules().rule, 1)
            self.assertEqual(GameOverRules().rule, 1)
        choose.assert_not_called()

    def test_rule_one_ignores_health_and_rule_two_ignores_idle_time(self):
        first, second = GameOverRules(rule=1), GameOverRules(rule=2)
        first.health = 0
        second.remaining = 0
        self.assertTrue(first.is_over)
        self.assertFalse(second.is_over)

    def test_only_selected_timer_advances_and_maze_entry_keeps_rule(self):
        first, second = GameOverRules(rule=1), GameOverRules(rule=2)
        first.update(2)
        second.update(3)
        self.assertEqual((first.remaining, first.health), (1, 3))
        self.assertEqual((second.remaining, second.health), (3, 2))
        first.record_action(2)
        self.assertEqual(first.remaining, 2)
        second.enter_maze(100)
        self.assertEqual(second.rule, 2)
        second.update(102)
        self.assertEqual(second.health, 2)
