"""임시 전투의 실제 입력, FIFO, 시간 기반 표시 및 순환 전환 검증."""
# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다. 커밋은 관련 코드 3개·변경 10줄 이내.
import unittest
import math
from collections import deque
from types import SimpleNamespace
from unittest.mock import Mock, patch

from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_UP, SDLK_DOWN
from codes.animation import Animation
from codes.battle import BattleMode
from codes.enemy import Enemy
from codes.game_framework import GameFramework
from codes.gameover import GameOverRules
from codes.maze_gamemode import MazeMode
from codes.menu_modes import create_menus


def assets():
    return SimpleNamespace(font=Mock(), timeout_font=Mock(),
                           maze_sheet=Mock(w=800, h=400),
                           character_sheet=Mock(w=600, h=600),
                           character_attack_sheet=Mock(w=800, h=400),
                           enemy_sheet=Mock(w=600, h=600),
                           effect_sheet=Mock(w=800, h=400),
                           yellow_arrow_sheet=Mock(w=2172, h=724),
                           effect_attack_sheet=Mock(w=800, h=200))


def press(mode, key):
    mode.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=key))
    mode.handle_event(SimpleNamespace(type=SDL_KEYUP, key=key))


class BattleTests(unittest.TestCase):
    def setUp(self):
        self.assets = assets()
        self.mode = BattleMode(self.assets)
        self.mode.framework = Mock(modes={'maze_mode': Mock()})
        with patch('codes.battle.get_time', return_value=0):
            self.mode.enter(True)
        self.mode.enemy.directions = deque(['left', 'up', 'right', 'down', 'left'])

    def test_frame_duration_tracks_maximum_not_remaining_timer(self):
        rules = self.mode.rules
        for maximum, expected in ((3, .15), (2, .1125), (1, .075), (0, .075), (10, .15)):
            rules.max_idle_time = maximum
            rules.remaining = .01
            self.assertAlmostEqual(rules.animation_frame_seconds, expected)
        animation = Animation([(0, 0), (0, 1)], 5, .5)
        self.assertEqual(animation.frame(5.499), (0, 0))
        self.assertEqual(animation.frame(5.5), (0, 1))
        self.assertTrue(animation.finished(100))
        self.assertEqual(animation.frame(100), (0, 1))

    def test_enemy_advances_on_fast_input_and_preserves_fifo(self):
        enemy = self.mode.enemy
        self.assertTrue(enemy.advance(0, .5))
        self.assertEqual(enemy.state, 'prepare')
        self.assertEqual(enemy.direction, 'left')
        self.assertEqual(len(enemy.directions), 5)
        self.assertTrue(enemy.advance(.01, .15))
        self.assertEqual(enemy.state, 'attack')
        self.assertEqual(list(enemy.directions), ['up', 'right', 'down', 'left'])
        self.assertTrue(enemy.advance(.02, .15))
        self.assertEqual(enemy.direction, 'up')
        self.assertEqual(enemy.animation.frame(.02), (1, 0))
        self.assertEqual(enemy.animation.frame(.379), (1, 0))
        self.assertEqual(enemy.animation.frame(.381), (1, 1))

    def test_refill_keeps_last_direction_and_never_exceeds_five(self):
        enemy = Enemy(0, .5)
        enemy.directions = deque(['left', 'up'])
        enemy.advance(0, .5)
        enemy.advance(1, .5)
        self.assertEqual(len(enemy.directions), 5)
        self.assertEqual(enemy.directions[0], 'up')
        enemy.refill()
        self.assertEqual(len(enemy.directions), 5)

    def test_fast_input_immediately_replaces_action_and_advances_enemy(self):
        press(self.mode, SDLK_LEFT)
        started = self.mode.player_animation.started
        self.mode.update(.1)
        press(self.mode, SDLK_LEFT)
        self.assertEqual(self.mode.successes, 2)
        self.assertGreater(self.mode.player_animation.started, started)
        self.assertEqual(self.mode.enemy.state, 'attack')
        self.assertEqual(self.mode.player_state, 'parry')
        self.assertEqual(self.mode.visual_state, 'parry')
        self.assertIsNotNone(self.mode.player_effect)
        self.mode.update(.11)
        press(self.mode, SDLK_UP)
        self.assertEqual(self.mode.visual_state, 'dodge_up')
        self.assertEqual(self.mode.player_animation.started, .11)

    def test_wrong_attack_cancels_increment_only_and_repeat_does_not_count(self):
        press(self.mode, SDLK_LEFT)
        press(self.mode, SDLK_LEFT)
        self.assertEqual(self.mode.successes, 2)
        self.mode.handle_event(SimpleNamespace(type=SDL_KEYDOWN, key=SDLK_LEFT, repeat=1))
        self.assertEqual(self.mode.successes, 2)

    def test_ten_successes_clear_back_to_maze_with_health_and_score(self):
        self.mode.rules.health = 2
        self.mode.enemy.directions = deque(['left'] * 5)
        with patch('codes.enemy.random.choice', return_value='left'):
            for index in range(10):
                press(self.mode, SDLK_LEFT if index % 2 == 0 else SDLK_RIGHT)
        self.assertEqual(self.mode.successes, 10)
        self.assertTrue(self.mode.cleared)
        self.mode.framework.change_mode.assert_called_once_with('maze_mode')
        self.assertEqual(self.mode.framework.modes['maze_mode'].pending_session,
                         (self.mode.rules, self.mode.score))

    def test_wrong_defense_subtracts_time_and_displays_hit_frames(self):
        press(self.mode, SDLK_LEFT)
        self.mode.update(2)
        press(self.mode, SDLK_UP)
        self.assertEqual(self.mode.enemy.state, 'attack')
        self.assertEqual(self.mode.player_state, 'hit')
        self.assertEqual(self.mode.rules.remaining, 1.5)
        self.mode.update(2.01)
        self.assertEqual(self.mode.visual_state, 'hit')
        self.assertEqual(self.mode.player_animation.frame(2.01), (0, 2))
        self.assertEqual(self.mode.player_animation.frame(2.149), (0, 2))
        self.assertEqual(self.mode.player_animation.frame(2.151), (0, 3))

    def test_horizontal_repeated_input_succeeds_without_failure(self):
        self.mode.enemy.directions[0] = 'right'
        press(self.mode, SDLK_LEFT)
        self.mode.update(.1)
        press(self.mode, SDLK_LEFT)
        self.assertEqual(self.mode.enemy.state, 'attack')
        self.assertEqual(self.mode.successes, 2)
        self.assertEqual(self.mode.next_attack_direction, 'right')
        self.assertEqual(self.mode.visual_state, 'parry')
        self.assertIsNone(self.mode.failure_started)
        self.assertAlmostEqual(self.mode.rules.remaining, 3)

    def test_opposite_horizontal_direction_also_succeeds(self):
        press(self.mode, SDLK_LEFT)
        self.mode.update(.1)
        press(self.mode, SDLK_RIGHT)
        self.assertEqual(self.mode.successes, 2)
        self.assertEqual(self.mode.visual_state, 'parry')
        self.assertAlmostEqual(self.mode.rules.remaining, 3)

    def test_wrong_attack_order_with_horizontal_parry_uses_attack_motion(self):
        self.mode.enemy.directions[0] = 'right'
        press(self.mode, SDLK_UP)
        self.mode.update(.1)
        press(self.mode, SDLK_RIGHT)
        self.assertEqual(self.mode.player_state, 'parry')
        self.assertEqual(self.mode.visual_state, 'parry')
        self.assertFalse(self.mode.player_animation.loop)
        self.assertEqual(self.mode.successes, 1)
        self.assertEqual(self.mode.next_attack_direction, 'left')
        self.assertIsNotNone(self.mode.player_effect)
        self.assertEqual(self.mode.rules.health, 3)
        self.assertEqual(self.mode.rules.remaining, 3)
        with patch('codes.hud.draw_rectangle'):
            self.mode.draw()
        self.assets.character_sheet.clip_draw.assert_not_called()
        self.assets.character_attack_sheet.clip_composite_draw.assert_not_called()
        self.assets.character_attack_sheet.clip_draw.assert_called_once_with(
            0, 0, 200, 200, 240, 200, 130, 130)

    def test_horizontal_attack_and_parry_draws_pressed_direction_attack(self):
        for incoming, key, required in (('left', SDLK_LEFT, 'left'),
                                        ('right', SDLK_RIGHT, 'right'),
                                        ('left', SDLK_LEFT, 'right'),
                                        ('right', SDLK_RIGHT, 'left')):
            with self.subTest(incoming=incoming, required=required):
                self.setUp()
                self.mode.enemy.directions[0] = incoming
                press(self.mode, SDLK_UP)
                self.mode.next_attack_direction = required
                self.mode.failure_started = self.mode.now - .1  # 성공 시 이전 실패 회전도 취소한다.
                press(self.mode, key)
                self.assertTrue(self.mode.horizontal_attack_parry)
                for column in range(4):
                    self.mode.update(column * .15 + .001)
                    self.assertEqual(self.mode.failure_rotation(), 0.0)
                    self.assets.character_attack_sheet.reset_mock()
                    with patch('codes.hud.draw_rectangle'):
                        self.mode.draw()
                    sheet = self.assets.character_attack_sheet
                    sheet.clip_composite_draw.assert_not_called()
                    call = (sheet.clip_composite_draw.call_args if sheet.clip_composite_draw.called
                            else sheet.clip_draw.call_args)
                    self.assertEqual(call.args[:4], (column * 200, 200 if incoming == 'left' else 0, 200, 200))
                self.assets.character_sheet.clip_draw.assert_not_called()
                self.assets.character_attack_sheet.clip_composite_draw.assert_not_called()
                self.mode.update(.61)
                press(self.mode, SDLK_UP)
                self.assertFalse(self.mode.horizontal_attack_parry)

    def test_vertical_failed_defense_removes_one_health_and_half_second(self):
        for incoming, wrong_key in (('up', SDLK_DOWN), ('up', SDLK_LEFT),
                                    ('up', SDLK_RIGHT), ('down', SDLK_UP),
                                    ('down', SDLK_LEFT), ('down', SDLK_RIGHT)):
            with self.subTest(incoming=incoming, wrong_key=wrong_key):
                self.setUp()
                self.mode.enemy.directions[0] = incoming
                press(self.mode, SDLK_UP if incoming == 'up' else SDLK_DOWN)
                self.assertEqual(self.mode.rules.health, 3)
                self.mode.update(.1)
                press(self.mode, wrong_key)
                self.assertEqual(self.mode.rules.health, 2)
                self.assertEqual(self.mode.rules.remaining, 2.5)
                self.assertEqual(self.mode.visual_state, 'hit')
                self.assertEqual(self.mode.failure_started, .1)

    def test_last_health_vertical_hit_ends_battle_even_on_tenth_attack(self):
        self.mode.enemy.directions[0] = 'up'
        press(self.mode, SDLK_UP)
        self.mode.rules.health = 1
        self.mode.successes = 9
        press(self.mode, SDLK_LEFT)
        self.assertEqual(self.mode.successes, 10)
        self.assertTrue(self.mode.is_game_over)
        self.assertEqual(self.mode.rules.health, 0)
        self.assertEqual(self.mode.rules.remaining, 0)
        self.assertEqual(self.mode.visual_state, 'hit')
        self.assertFalse(self.mode.cleared)
        self.mode.framework.change_mode.assert_not_called()

    def test_correct_horizontal_parries_and_vertical_dodges(self):
        for direction, key in (('left', SDLK_LEFT), ('up', SDLK_UP), ('down', SDLK_DOWN)):
            with self.subTest(direction=direction):
                self.setUp()
                self.mode.enemy.directions[0] = direction
                press(self.mode, key)
                self.mode.update(2)
                press(self.mode, key)
                self.assertEqual(self.mode.player_state,
                                 'parry' if direction == 'left' else 'dodge_' + direction)
                self.assertEqual(self.mode.rules.remaining, 2)
                self.assertEqual(self.mode.rules.health, 3)

    def test_lethal_hit_still_selects_hit_image_and_stops_clear(self):
        press(self.mode, SDLK_LEFT)
        self.mode.update(2)
        self.mode.rules.remaining = .1
        self.mode.rules.ACTION_BONUS = 0
        press(self.mode, SDLK_UP)
        self.assertTrue(self.mode.is_game_over)
        self.assertEqual(self.mode.visual_state, 'hit')
        self.assertEqual(self.mode.player_animation.frame(2), (0, 2))
        self.mode.framework.change_mode.assert_not_called()

    def test_time_alone_never_advances_enemy_or_consumes_queue(self):
        press(self.mode, SDLK_LEFT)
        before = tuple(self.mode.enemy.directions)
        self.mode.update(2)
        self.assertEqual(self.mode.enemy.state, 'prepare')
        self.assertEqual(tuple(self.mode.enemy.directions), before)

    def test_prepare_draws_direction_above_enemy_only(self):
        press(self.mode, SDLK_LEFT)
        with patch('codes.hud.draw_rectangle'):
            self.mode.draw()
        self.assets.effect_sheet.clip_draw.assert_any_call(0, 0, 200, 200, 350, 465, 65, 65)
        self.assets.effect_sheet.reset_mock()
        self.mode.update(2)
        press(self.mode, SDLK_LEFT)
        with patch('codes.hud.draw_rectangle'):
            self.mode.draw()
        self.assertFalse(any(call.args[4:6] == (350, 465)
                             for call in self.assets.effect_sheet.clip_draw.call_args_list))

    def test_two_mazes_battle_maze_cycle_and_fifteen_second_deadline(self):
        with patch('codes.maze_gamemode.get_time', return_value=0), \
             patch('codes.battle.get_time', return_value=0):
            maze = MazeMode(self.assets)
            modes = create_menus(self.assets.font)
            modes.update(maze_mode=maze, battle_mode=self.mode)
            framework = GameFramework(modes, clock=lambda: 0)
            for mode in modes.values():
                mode.framework = framework
            framework.change_mode('maze_mode')
            maze.player.rules.health = 2
            for _ in range(2):
                maze.update(0)
                maze.player.position = (0, 0)
                maze.maze.walls.pop((0, 1), None)
                maze.maze.exit = (0, 1)
                press(maze, SDLK_RIGHT)
                self.assertFalse(maze.awaiting_next_maze)  # 첫 전투 전에는 제약 없이 자동 전환한다.
            self.assertFalse(maze.awaiting_next_maze)
            self.assertEqual(framework.current_mode, 'battle_mode')
            self.assertEqual(self.mode.rules.health, 2)
            self.mode.enemy.directions = deque(['left'] * 5)
            # 적 방향 고정 중에도 제약은 유효한 후보 중 하나로 선택한다.
            with patch('codes.enemy.random.choice', side_effect=lambda options: options[0]):
                for index in range(10):
                    press(self.mode, SDLK_LEFT if index % 2 == 0 else SDLK_RIGHT)
            framework.update(framework.notice.DURATION)
            self.assertEqual(framework.current_mode, 'maze_mode')
            self.assertEqual(maze.completed, 0)
            self.assertEqual(len(framework.notice.active), 1)
            self.assertEqual(maze.player.rules.health, 2)
            with patch('codes.constraints.random.choice', return_value='battle_rhythm'):
                framework.change_mode('battle_mode')
            framework.update(framework.notice.DURATION)
            self.mode.rules.remaining = 100
            framework.update(15)
            self.assertFalse(framework.stage_timed_out)  # 리듬 제약은 제한 시계를 멈춘다.
            self.assertEqual(self.mode.rules.remaining, 100)
            self.assertTrue(self.mode.is_game_over)  # 누락 박자의 체력 피해는 유지한다.

    def test_attacks_must_alternate_and_dodge_does_not_change_order(self):
        self.assertEqual(self.mode.next_attack_direction, 'left')
        for key, count, expected in ((SDLK_RIGHT, 0, 'left'),
                                     (SDLK_LEFT, 1, 'right'),
                                     (SDLK_LEFT, 1, 'right'),
                                     (SDLK_UP, 1, 'right'),
                                     (SDLK_RIGHT, 2, 'left'),
                                     (SDLK_LEFT, 3, 'right')):
            press(self.mode, key)
            self.assertEqual(self.mode.successes, count)
            self.assertEqual(self.mode.next_attack_direction, expected)

    def test_yellow_arrow_points_opposite_last_successful_attack(self):
        for key, column in ((SDLK_LEFT, 1), (SDLK_RIGHT, 0)):
            press(self.mode, key)
            self.assets.yellow_arrow_sheet.reset_mock()
            with patch('codes.hud.draw_rectangle'):
                self.mode.draw()
            call = self.assets.yellow_arrow_sheet.clip_draw.call_args.args
            self.assertEqual(call[:4], (column * 543, 0, 543, 724))
            self.assertEqual(call[4:6], (240, 295))

    def test_wrong_order_shows_cross_and_smooth_right_rotation_without_blocking(self):
        press(self.mode, SDLK_RIGHT)
        self.assertEqual(self.mode.successes, 0)
        for now, angle in ((0, 0), (.15, -math.radians(7.5)),
                           (.3, -math.radians(15)), (.45, -math.radians(7.5)), (.6, 0)):
            self.mode.update(now)
            self.assertAlmostEqual(self.mode.failure_rotation(), angle)
            self.assets.effect_sheet.reset_mock()
            with patch('codes.hud.draw_rectangle'):
                self.mode.draw()
            if angle:
                rendered = self.assets.character_sheet.clip_composite_draw.call_args.args
                self.assertAlmostEqual(rendered[4], angle)
                self.assertEqual(rendered[6:8], (240, 200))
            cross = (200, 200, 200, 200, 240, 230, 65, 65)
            calls = [call.args for call in self.assets.effect_sheet.clip_draw.call_args_list]
            self.assertEqual(cross in calls, now < .4)
        self.mode.update(.7)
        press(self.mode, SDLK_LEFT)
        self.assertEqual(self.mode.successes, 1)

    def test_reentry_resets_attack_order_and_failure_feedback(self):
        press(self.mode, SDLK_RIGHT)
        press(self.mode, SDLK_LEFT)
        with patch('codes.battle.get_time', return_value=1):
            self.mode.enter(False)
        self.assertEqual(self.mode.next_attack_direction, 'left')
        self.assertEqual(self.mode.successes, 0)
        self.assertIsNone(self.mode.failure_started)


if __name__ == '__main__':
    unittest.main()
