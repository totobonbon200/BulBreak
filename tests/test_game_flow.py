# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md의 최신 기준을 확인한다.
"""모드 전환과 미로 진행의 회귀 검증."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from pico2d import SDL_KEYDOWN, SDL_QUIT, SDLK_RIGHT, SDLK_UP, SDLK_LEFT, SDLK_DOWN
from codes.character import Character
from codes.constraints import CAT_CONSTRAINT, ConstraintNotice
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

    def test_maze_stays_playable_with_health_and_time_remaining(self):
        assets = SimpleNamespace(font=Mock(), maze_sheet=Mock(w=800, h=400),
                                 notice_font=Mock(), menu_image=Mock(),
                                 character_sheet=Mock(w=600, h=600), effect_sheet=Mock(w=800, h=400))
        with patch('codes.maze_gamemode.get_time', return_value=0):
            mode = MazeMode(assets)
            modes = create_menus(assets.font)
            modes['maze_mode'] = mode
            framework = GameFramework(modes, clock=lambda: 0)
            for item in modes.values():
                item.framework = framework
            framework.change_mode('maze_mode')
            mode.player.rules.health = 100
            mode.player.rules.remaining = 100
            framework.update(16)
            framework.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=SDLK_UP))
            self.assertTrue(mode.player.is_playing)

    def test_first_game_start_routes_through_tutorial_once(self):
        modes = {name: Mock() for name in GameFramework.MODES}
        modes['tutorial_mode'].completed = False
        framework = GameFramework(modes)
        framework.change_mode('maze_mode')
        self.assertEqual(framework.current_mode, 'tutorial_mode')
        self.assertTrue(framework.timer_paused)
        modes['tutorial_mode'].completed = True
        framework.change_mode('start_mode')
        framework.change_mode('maze_mode')
        self.assertEqual(framework.current_mode, 'maze_mode')

    def test_gameplay_keeps_updating_past_fifteen_seconds(self):
        modes = {name: Mock() for name in GameFramework.MODES if name != 'quit_mode'}
        framework = GameFramework(modes, clock=lambda: 20)
        for name in ('maze_mode', 'battle_mode'):
            framework.change_mode(name)
            framework.update(35)
            modes[name].update.assert_called_once_with(35)
            framework.change_mode('start_mode')

    def test_new_maze_keeps_regular_game_over_rules(self):
        with patch('codes.maze_gamemode.get_time', return_value=0):
            mode = MazeMode(Mock())
            modes = create_menus(Mock())
            modes['maze_mode'] = mode
            framework = GameFramework(modes, clock=lambda: 0)
            for item in modes.values():
                item.framework = framework
            framework.change_mode('maze_mode')
            mode.maze.walls.pop((0, 1), None)
            mode.maze.exit = (0, 1)
            mode.now = 14
            mode.player.rules.remaining = 100
            mode.player.rules.health = 100
            framework.clock = lambda: 14
            framework.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=SDLK_RIGHT))
            self.assertEqual(mode.completed, 1)
            self.assertEqual(mode.player.position, (0, 1))
            self.assertEqual(mode.player.action_state, 'idle')
            framework.update(15)
            self.assertTrue(mode.player.is_playing)
            mode.player.rules.health = 0
            mode.player.rules.rule = 2
            mode.player.update(15)
            framework.update(100)
            self.assertTrue(framework.game_over_active)

    def test_maze_constraint_starts_after_first_battle(self):
        # 최초 전투 진입은 생략하고 복귀 안내가 끝날 때 획득한다.
        notice = ConstraintNotice()
        self.assertFalse(notice.begin('maze_mode', 'battle_mode', 0))
        self.assertTrue(notice.begin('battle_mode', 'maze_mode', 0))
        self.assertIsNone(notice.finish(0.9))
        self.assertEqual(notice.active, set())
        self.assertEqual(notice.finish(1), 'maze_mode')
        self.assertEqual(len(notice.active), 1)  # 진입 모드의 제약 하나만 적용한다.
        self.assertTrue(notice.active <= {'maze_cross', CAT_CONSTRAINT, 'maze_darkness'})

    def test_constraints_accumulate_without_duplicates(self):
        notice = ConstraintNotice()
        for source, target in [('battle_mode', 'maze_mode'),
                               ('maze_mode', 'battle_mode'), ('battle_mode', 'maze_mode')]:
            notice.begin(source, target, 0)
            notice.finish(1)
        self.assertEqual(len(notice.active), 1)  # 전환을 반복해도 누적하지 않는다.
        notice.reset()
        self.assertEqual(notice.active, set())

    def test_cat_constraint_is_available_for_both_destinations(self):
        for source, target in (('battle_mode', 'maze_mode'), ('maze_mode', 'battle_mode')):
            notice = ConstraintNotice()
            notice.enabled = True
            with patch('codes.constraints.random.choice', return_value=CAT_CONSTRAINT) as choose:
                self.assertTrue(notice.begin(source, target, 0))
            self.assertIn(CAT_CONSTRAINT, choose.call_args.args[0])
            self.assertEqual(notice.finish(notice.DURATION), target)
            self.assertEqual(notice.active, {CAT_CONSTRAINT})

    def test_guide_round_trip_and_white_start_text(self):
        font = Mock()
        modes = create_menus(font)
        framework = GameFramework(modes)
        for mode in modes.values():
            mode.framework = framework
        framework.draw()
        self.assertEqual(len(font.draw.call_args_list), 4)
        framework.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=SDLK_DOWN))
        framework.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=SDLK_LEFT))
        self.assertEqual(framework.current_mode, 'guide_mode')
        guide = modes['guide_mode']
        self.assertEqual(guide.page, 0)
        framework.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=SDLK_DOWN))
        framework.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=SDLK_DOWN))
        self.assertEqual(guide.page, 2)
        framework.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=SDLK_UP))
        self.assertEqual(guide.page, 1)
        framework.update(100)
        with patch('codes.guide_mode.draw_line'):
            framework.draw()
        framework.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=SDLK_RIGHT))
        self.assertEqual(framework.current_mode, 'start_mode')
        framework.change_mode('guide_mode')
        self.assertEqual(guide.page, 0)

    def test_start_screen_confirms_game_start_and_quit(self):
        for index, expected in ((0, 'maze_mode'), (3, 'quit_mode')):
            menu = create_menus(Mock())['start_mode']
            menu.framework = Mock()
            menu.index = index
            menu.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=SDLK_LEFT))
            menu.framework.change_mode.assert_called_once_with(expected)

    def test_debug_menu_uses_vertical_selection_and_horizontal_actions(self):
        menu = create_menus(Mock())['instrument_mode']
        menu.framework = Mock()
        for key in (SDLK_DOWN, SDLK_LEFT, SDLK_RIGHT):
            menu.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=key))
        menu.framework.play_constraint.assert_called_once_with('battle_mode', 'battle_placeholder')
        menu.framework.change_mode.assert_called_once_with('start_mode')

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

    def test_maze_timer_ignores_input_and_resets_on_transition(self):
        player = Character((0, 0))
        player.update(2.5)
        player.react(2.5, 'blocked')
        self.assertEqual(player.idle_remaining(2.5), 0.5)
        player.enter_maze((1, 1), 100)
        self.assertEqual(player.idle_remaining(100), 3)
        player.update(101.5)
        self.assertTrue(player.is_playing)
        self.assertEqual(player.rules.health, 3)
        self.assertEqual(player.rules.max_idle_time, 3)

    def test_action_recovery_and_wrong_defense_use_remaining_time(self):
        rules = GameOverRules(rule=2)
        for now in (1, 2, 3, 4, 5):
            rules.record_action(now)
        self.assertEqual(rules.health, 3)
        rules.enter_maze(100)
        for now in (101, 102, 103):
            rules.record_action(now)
        self.assertEqual(rules.health, 2)
        self.assertEqual(rules.max_idle_time, 3)
        rules.enter_battle(103)
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
        assets = SimpleNamespace(font=Mock(), timeout_font=Mock(), cat_effect=None, main_image=None, menu_image=Mock(),
                                 notice_font=Mock(),
                                 maze_sheet=Mock(w=400, h=200),
                                 character_sheet=Mock(w=400, h=400), effect_sheet=Mock(w=800, h=400))
        key = lambda value: SimpleNamespace(type=SDL_KEYDOWN, key=value)
        events = [[key(SDLK_LEFT)], [], [],
                  [], [SimpleNamespace(type=SDL_QUIT)]]
        with patch.object(game, 'Assets', return_value=assets), \
             patch.object(game, 'TutorialMode', return_value=SimpleNamespace(completed=True)), \
             patch.object(game, 'get_time', side_effect=[0, .1, .2, 10, 10.1]), \
             patch.object(game, 'get_events', side_effect=events), \
             patch.object(game, 'clear_canvas'), patch.object(game, 'update_canvas'), \
             patch.object(game, 'draw_rectangle') as background, \
             patch.object(game, 'delay'), patch('pico2d.draw_rectangle'), \
             patch('codes.menu_modes.draw_start_panel'), \
             patch('codes.maze_gamemode.get_time', return_value=0):
            game.main()
        background.assert_called_with(0, 0, 799, 599, 0, 0, 0, 255, filled=True)
        self.assertEqual(assets.maze_sheet.opacify.call_args_list[-1].args, (1.0,))


if __name__ == '__main__':
    unittest.main()
