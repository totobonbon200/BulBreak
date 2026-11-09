"""모드 전환과 미로 진행의 회귀 검증."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from pico2d import SDL_KEYDOWN, SDL_QUIT, SDLK_RIGHT, SDLK_UP, SDLK_LEFT
from codes.character import Character
from codes.game_framework import GameFramework
from codes.gameover import GameOverRules
from codes.maze import Maze
from codes import main as game


class GameFlowTests(unittest.TestCase):
    def test_mode_history_and_reentry(self):
        modes = {name: Mock() for name in GameFramework.MODES if name != 'quit_mode'}
        framework = GameFramework(modes)
        modes['start_mode'].enter.assert_called_once_with(True)
        framework.change_mode('maze_mode')
        self.assertEqual(framework.previous_mode, 'start_mode')
        framework.change_mode('start_mode')
        modes['start_mode'].enter.assert_called_with(False)
        framework.change_mode('quit_mode')
        self.assertFalse(framework.running)

    def test_timer_recovers_one_second_and_pauses_on_transition(self):
        player = Character((0, 0))
        player.update(2.5)
        player.react(2.5, 'blocked')
        self.assertEqual(player.idle_remaining(2.5), 1.5)
        player.enter_maze((1, 1), 100)
        self.assertEqual(player.idle_remaining(100), 1.5)
        player.update(101.5)
        self.assertFalse(player.is_playing)

    def test_health_penalty_occurs_once_per_maze(self):
        rules = GameOverRules()
        for now in (1, 2, 3, 4, 5):
            rules.record_action(now)
        self.assertEqual(rules.health, 2)
        rules.enter_maze(100)
        for now in (101, 102, 103):
            rules.record_action(now)
        self.assertEqual(rules.health, 1)
        rules.record_wrong_defense()
        self.assertTrue(rules.is_over)

    def test_wall_hits_and_action_animation(self):
        maze = Maze(4)
        maze.walls = {(0, 1): 2}
        player = Character((0, 0))
        for now, expected in ((0.1, 'hit'), (0.2, 'broken')):
            player.position, result = maze.step(player.position, (0, 1))
            self.assertEqual(result, expected)
            player.react(now, result)
            self.assertEqual(player.action_state, 'wall_attack')
            self.assertEqual(player.position, (0, 0))
        player.position, result = maze.step(player.position, (0, 1))
        player.react(0.3, result)
        self.assertEqual(player.action_state, 'moving')
        self.assertEqual(player.position, (0, 1))
        player.update(0.7)
        self.assertEqual(player.action_state, 'idle')

    def test_main_menu_instructions_maze_and_overlay(self):
        assets = SimpleNamespace(font=Mock(), maze_sheet=Mock(w=400, h=200),
                                 character_sheet=Mock(w=400, h=400))
        key = lambda value: SimpleNamespace(type=SDL_KEYDOWN, key=value)
        events = [[key(SDLK_UP)], [key(SDLK_LEFT)], [key(SDLK_RIGHT)],
                  [], [SimpleNamespace(type=SDL_QUIT)]]
        with patch.object(game, 'Assets', return_value=assets), \
             patch.object(game, 'get_time', side_effect=[0, .1, .2, 4, 4.1]), \
             patch.object(game, 'get_events', side_effect=events), \
             patch.object(game, 'clear_canvas'), patch.object(game, 'update_canvas'), \
             patch.object(game, 'delay'), patch('pico2d.draw_rectangle'), \
             patch('codes.maze_gamemode.get_time', return_value=0):
            game.main()
        assets.maze_sheet.clip_draw.assert_any_call(300, 100, 100, 100,
                                                   400, 300, 800, 600)
        self.assertEqual(assets.maze_sheet.opacify.call_args_list[-1].args, (1.0,))


if __name__ == '__main__':
    unittest.main()
