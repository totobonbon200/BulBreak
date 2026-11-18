# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from codes.hud import draw_hud, draw_timer
from codes.gameover import GameOverRules


class HealthDisplayTests(unittest.TestCase):
    def test_timer_fills_white_when_paused(self):
        rules = GameOverRules()
        with patch('codes.hud.draw_rectangle') as rectangle:
            draw_timer(rules, 1.5, paused=False)
            rectangle.assert_called_with(542, 481, 648, 510, 255, 220, 0, filled=True)
            draw_timer(rules, 1.5, paused=True)
            rectangle.assert_called_with(542, 481, 754, 510, 255, 255, 255, filled=True)

    def test_empty_health_appears_from_right_and_uses_top_row(self):
        for health in range(4):
            assets = SimpleNamespace(font=Mock(), effect_sheet=Mock(w=800, h=400))
            assets.notice_font, assets.menu_image = Mock(), Mock()
            rules = GameOverRules()
            rules.health = health
            with patch('codes.hud.draw_rectangle'):
                draw_hud(assets, rules, 0, 0)
            calls = assets.effect_sheet.clip_draw.call_args_list
            self.assertEqual([call.args[0] for call in calls],
                             [0 if i < health else 200 for i in range(3)])
            self.assertTrue(all(call.args[1:4] == (200, 200, 200) for call in calls))
