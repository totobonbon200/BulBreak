import unittest
from unittest.mock import patch
from codes.gameover import GameOverRules


class GameOverRuleTests(unittest.TestCase):
    def test_new_play_uses_fixed_rule_without_random_selection(self):
        with patch('codes.gameover.random.choice', side_effect=AssertionError('무작위 추첨 금지')) as choose:
            self.assertEqual(GameOverRules().rule, 1)
            self.assertEqual(GameOverRules().rule, 1)
        choose.assert_not_called()

    def test_health_depletion_ends_play_but_timer_requires_update(self):
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
        self.assertEqual(second.max_idle_time, 2.95)


class DeadlineTests(unittest.TestCase):
    def test_maximum_stops_at_one_second_and_restart_restores_three(self):
        rules = GameOverRules()
        for index in range(60):
            rules.enter_maze(index + 100)
        self.assertEqual(rules.max_idle_time, 1)
        self.assertEqual(rules.remaining, 1)
        self.assertEqual(rules.health, 3)
        self.assertEqual(GameOverRules().max_idle_time, 3)

    def test_long_idle_consumes_all_health_and_cannot_be_revived_by_input(self):
        rules = GameOverRules()
        rules.update(9)
        self.assertTrue(rules.is_over)
        rules.record_action(10)
        self.assertEqual((rules.health, rules.remaining), (0, 0))
