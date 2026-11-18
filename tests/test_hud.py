# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from codes.hud import draw_hud
from codes.gameover import GameOverRules


class HealthDisplayTests(unittest.TestCase):
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
