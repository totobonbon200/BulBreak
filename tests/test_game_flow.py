"""모드 전환과 미로 진행의 회귀 검증."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from pico2d import SDL_KEYDOWN, SDL_QUIT, SDLK_RIGHT, SDLK_UP, SDLK_LEFT, SDLK_DOWN
from codes.character import Character
from codes.game_framework import GameFramework
from codes.gameover import GameOverRules
from codes.maze import Maze
from codes import main as game
from codes.maze_gamemode import MazeMode
from codes.menu_modes import create_menus


class GameFlowTests(unittest.TestCase):
    def setUp(self):
        drawing = patch('codes.hud.draw_rectangle')
        drawing.start()
        self.addCleanup(drawing.stop)

    def test_stage_deadline_ignores_input_and_shows_large_korean_message(self):
        assets = SimpleNamespace(font=Mock(), maze_sheet=Mock(w=800, h=400),
                                 character_sheet=Mock(w=600, h=600), effect_sheet=Mock(w=800, h=400))
        with patch('codes.maze_gamemode.get_time', return_value=0):
            mode = MazeMode(assets)
            modes = create_menus(assets.font)
            modes['maze_mode'] = mode
            large_font = Mock()
            framework = GameFramework(modes, timeout_font=large_font, clock=lambda: 0)
            for item in modes.values():
                item.framework = framework
            framework.change_mode('maze_mode')
            mode.player.rules.rule = 3
            framework.restart_stage_timer()
            mode.player.rules.health = 100
            mode.player.rules.remaining = 100
            framework.update(14.9)
            framework.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=SDLK_UP))
            self.assertFalse(framework.stage_timed_out)
            framework.update(15)
            self.assertTrue(framework.stage_timed_out)
            self.assertFalse(mode.player.is_playing)
            self.assertEqual(framework.stage_elapsed, 15)
            with patch('pico2d.draw_rectangle'):
                framework.draw()
            large_font.draw.assert_called_once_with(
                100, 380, '관심받고싶음? 옛다 관심', (255, 255, 255))
            self.assertNotIn('GAME OVER', mode.message)
            framework.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=SDLK_RIGHT))
            self.assertFalse(mode.player.is_playing)
            framework.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=SDLK_DOWN))
            self.assertFalse(framework.stage_timed_out)
            self.assertTrue(mode.player.is_playing)
            self.assertEqual(framework.stage_elapsed, 0)

    def test_stage_timer_only_runs_in_gameplay_and_resets_on_entry(self):
        modes = {name: Mock() for name in GameFramework.MODES if name != 'quit_mode'}
        framework = GameFramework(modes, clock=lambda: 20)
        framework.update(100)
        self.assertIsNone(framework.stage_started)
        for name in ('maze_mode', 'battle_mode'):
            modes[name].use_stage_deadline = True
            framework.change_mode(name)
            framework.update(34.9)
            self.assertFalse(framework.stage_timed_out)
            framework.update(35)
            self.assertTrue(framework.stage_timed_out)
            modes[name].on_stage_timeout.assert_called_once()
            framework.change_mode('start_mode')
            self.assertFalse(framework.stage_timed_out)

    def test_new_maze_resets_deadline_and_existing_game_over_is_preserved(self):
        with patch('codes.maze_gamemode.get_time', return_value=0):
            mode = MazeMode(Mock())
            modes = create_menus(Mock())
            modes['maze_mode'] = mode
            framework = GameFramework(modes, clock=lambda: 0)
            for item in modes.values():
                item.framework = framework
            framework.change_mode('maze_mode')
            mode.maze.walls.pop((0, 1), None)
            mode.player.rules.rule = 3
            mode.maze.exit = (0, 1)
            mode.now = 14
            mode.player.rules.remaining = 100
            mode.player.rules.health = 100
            framework.clock = lambda: 14
            framework.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=SDLK_RIGHT))
            self.assertEqual(mode.completed, 1)
            self.assertEqual(framework.stage_started, 14)
            framework.update(15)
            self.assertFalse(framework.stage_timed_out)
            self.assertEqual(framework.stage_elapsed, 1)
            mode.player.rules.health = 0
            mode.player.rules.rule = 2
            mode.player.update(15)
            framework.update(100)
            self.assertFalse(framework.stage_timed_out)

    def test_guide_round_trip_and_black_start_text(self):
        font = Mock()
        modes = create_menus(font)
        framework = GameFramework(modes)
        for mode in modes.values():
            mode.framework = framework
        framework.draw()
        self.assertTrue(all(call.args[-1] == (0, 0, 0)
                            for call in font.draw.call_args_list))
        framework.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=SDLK_LEFT))
        self.assertEqual(framework.current_mode, 'guide_mode')
        framework.update(100)
        framework.draw()
        framework.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=SDLK_RIGHT))
        self.assertEqual(framework.current_mode, 'start_mode')

    def test_start_screen_down_starts_and_up_quits(self):
        for key, expected in ((SDLK_DOWN, 'maze_mode'), (SDLK_UP, 'quit_mode')):
            menu = create_menus(Mock())['start_mode']
            menu.framework = Mock()
            menu.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=key))
            menu.framework.change_mode.assert_called_once_with(expected)

    def test_game_over_restart_resets_session_and_blocks_held_key(self):
        with patch('codes.maze_gamemode.get_time', return_value=10):
            mode = MazeMode(Mock())
            old_maze = mode.maze
            mode.completed = 8
            mode.player.rules.rule = 2
            mode.player.rules.health = 0
            mode.player.update(10)
            event = SimpleNamespace(type=SDL_KEYDOWN, key=SDLK_DOWN)
            mode.handle_event(event)
            self.assertIsNot(mode.maze, old_maze)
            self.assertEqual(mode.completed, 0)
            self.assertTrue(mode.player.is_playing)
            self.assertEqual(mode.player.rules.health, 3)
            self.assertEqual(mode.player.idle_remaining(10), 3)
            self.assertEqual(mode.player.position, mode.maze.entrance)
            mode.update(10.1)
            mode.handle_event(event)
            self.assertEqual(mode.player.position, mode.maze.entrance)
            self.assertEqual(mode.player.action_state, 'idle')

    def test_game_over_up_returns_and_next_start_is_fresh(self):
        with patch('codes.maze_gamemode.get_time', return_value=10):
            mode = MazeMode(Mock())
            mode.framework = Mock()
            mode.player.rules.rule = 2
            mode.player.rules.health = 0
            mode.player.update(10)
            mode.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=SDLK_UP))
            mode.framework.change_mode.assert_called_once_with('start_mode')
            mode.enter(False)
            self.assertTrue(mode.player.is_playing)
            self.assertEqual(mode.player.rules.health, 3)

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
        self.assertTrue(player.is_playing)
        self.assertEqual(player.rules.health, 2)
        self.assertEqual(player.rules.max_idle_time, 2.95)

    def test_action_recovery_and_wrong_defense_use_remaining_time(self):
        rules = GameOverRules(rule=2)
        for now in (1, 2, 3, 4, 5):
            rules.record_action(now)
        self.assertEqual(rules.health, 3)
        rules.enter_maze(100)
        for now in (101, 102, 103):
            rules.record_action(now)
        self.assertEqual(rules.health, 3)
        self.assertEqual(rules.max_idle_time, 2.95)
        rules.remaining = 0.5
        rules.record_wrong_defense()
        self.assertTrue(rules.is_over)

    def test_regular_input_preserves_health_and_recovers_time(self):
        rules = GameOverRules(rule=2)
        for now in range(1, 10):
            rules.record_action(now)
            self.assertEqual(rules.health, 3)
            self.assertEqual(rules.remaining, 3)
        self.assertFalse(rules.is_over)

    def test_health_timer_preserves_remainder_after_delayed_update(self):
        rules = GameOverRules(rule=2)
        rules.update(6.5)
        self.assertEqual(rules.health, 1)
        self.assertEqual(rules.remaining, 2.5)

    def test_wall_hits_and_action_animation(self):
        maze = Maze(6)
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

    def test_wall_attack_lunges_in_each_direction_and_returns(self):
        maze = Mock(cell_size=100)
        maze.center.return_value = (400, 300)
        for result in ('hit', 'broken'):
            for row, column in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                with self.subTest(result=result, direction=(row, column)):
                    player = Character((1, 1))
                    sheet = Mock(w=400, h=400)
                    player.react(0, result, (row, column))
                    for now, frame, offset in ((0, 1, 0), (.075, 1, 10),
                                               (.15, 0, 20), (.225, 0, 10),
                                               (.3, 0, 0)):
                        player.update(now)
                        player.draw(sheet, maze, now)
                        args = sheet.clip_composite_draw.call_args.args
                        self.assertEqual(args[:4], (frame * 100, 300, 100, 100))
                        self.assertEqual(args[4:6], (0, 'h' if column == -1 else ''))
                        self.assertAlmostEqual(args[6], 400 + column * offset)
                        self.assertAlmostEqual(args[7], 300 - row * offset)
                        self.assertEqual(player.position, (1, 1))
                    self.assertEqual(player.action_state, 'idle')

    def test_maze_passes_wall_attack_direction(self):
        with patch('codes.maze_gamemode.get_time', return_value=0):
            mode = MazeMode(Mock())
        mode.maze.walls = {(0, 1): 2}
        mode.player.position = (0, 0)
        mode.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=SDLK_RIGHT))
        self.assertEqual(mode.player.action_state, 'wall_attack')
        self.assertEqual(mode.player.attack_direction, (0, 1))

    def test_main_menu_instructions_maze_and_overlay(self):
        assets = SimpleNamespace(font=Mock(), timeout_font=Mock(), maze_sheet=Mock(w=400, h=200),
                                 character_sheet=Mock(w=400, h=400), effect_sheet=Mock(w=800, h=400))
        key = lambda value: SimpleNamespace(type=SDL_KEYDOWN, key=value)
        events = [[key(SDLK_RIGHT)], [key(SDLK_LEFT)], [key(SDLK_DOWN)],
                  [], [SimpleNamespace(type=SDL_QUIT)]]
        with patch.object(game, 'Assets', return_value=assets), \
             patch.object(game, 'get_time', side_effect=[0, .1, .2, 10, 10.1]), \
             patch.object(game, 'get_events', side_effect=events), \
             patch.object(game, 'clear_canvas'), patch.object(game, 'update_canvas'), \
             patch.object(game, 'draw_rectangle') as background, \
             patch.object(game, 'delay'), patch('pico2d.draw_rectangle'), \
             patch('codes.maze_gamemode.get_time', return_value=0):
            game.main()
        background.assert_called_with(0, 0, 799, 599, 0, 0, 0, 255, filled=True)
        self.assertEqual(assets.maze_sheet.opacify.call_args_list[-1].args, (1.0,))


if __name__ == '__main__':
    unittest.main()
