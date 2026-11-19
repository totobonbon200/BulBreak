# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""중앙 미로와 리듬 제약의 경계·피해 회귀 검증."""
import unittest
from unittest.mock import Mock, patch
from types import SimpleNamespace
from codes.cross_maze import CrossMaze
from codes.rhythm import Rhythm
from codes.rhythm_countdown import RhythmCountdown
from codes.constraints import ConstraintNotice
from test_battle import assets, press
from codes.maze_gamemode import MazeMode
from codes.battle import BattleMode
from pico2d import SDLK_LEFT, SDLK_RIGHT, SDLK_UP, SDLK_DOWN


class ConstraintTests(unittest.TestCase):
    def setUp(self):
        # 시간 경계 검증은 원본 전체 패턴으로 고정하고 무작위 선택은 별도 검증한다.
        original_sample = __import__('random').sample
        sampling = patch('codes.rhythm.random.sample', side_effect=lambda patterns, count:
                         patterns if patterns and isinstance(patterns[0], list) else original_sample(patterns, count))
        sampling.start()
        self.addCleanup(sampling.stop)

    def test_cross_has_five_cells_and_only_exit_moves(self):
        maze = CrossMaze()
        self.assertEqual(len(maze.walls), 3)
        self.assertEqual(maze.entrance, (1, 1))
        for delta in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            position, result = maze.step(maze.entrance, delta)
            self.assertEqual(result == 'exit', position == maze.exit)

    def test_all_patterns_exact_hits_consume_one_beat(self):
        rhythm = Rhythm(0)
        self.assertEqual(len(rhythm.patterns), 10)
        for segment in range(10):
            for index, hit in enumerate(rhythm.hits):
                self.assertGreaterEqual(hit, 0)
                now = segment * 4 + 2 + hit / 1000
                self.assertEqual(rhythm.advance(now), 0)
                self.assertTrue(rhythm.press(now))
                self.assertEqual(rhythm.index, index + 1)
            self.assertEqual(rhythm.advance((segment + 1) * 4 + .001), 0)

    def test_timing_boundary_and_misses_consumed_once(self):
        for offset in (-.100, .100):
            self.assertTrue(Rhythm(0).press(2 + offset))
        self.assertFalse(Rhythm(0).press(2.101))
        rhythm = Rhythm(0)
        self.assertEqual(rhythm.advance(3.601), 4)
        self.assertEqual(rhythm.advance(3.601), 0)
        self.assertEqual(rhythm.frame(.5), (0, 1))
        self.assertEqual(rhythm.frame(.55), (0, 0))

    def test_six_cross_exits_keep_original_gameover_timer(self):
        mode = MazeMode(assets())
        notice = ConstraintNotice()
        notice.active.add('maze_cross')
        mode.framework = SimpleNamespace(notice=notice, restart_stage_timer=lambda: None)
        with patch('codes.maze_gamemode.get_time', return_value=0):
            mode.enter(False)
        keys = {(-1, 0): SDLK_UP, (1, 0): SDLK_DOWN, (0, -1): SDLK_LEFT, (0, 1): SDLK_RIGHT}
        for index in range(6):
            delta = tuple(a - b for a, b in zip(mode.maze.exit, mode.maze.entrance))
            press(mode, keys[delta])
            self.assertEqual(mode.completed, int(index == 5))
        self.assertEqual(mode.cross_count, 0)  # 여섯 번째 출구에서 다음 미로를 바로 시작한다.
        mode.update(mode.now + 9.1)
        self.assertTrue(mode.is_game_over)

    def test_demo_input_preserves_health_and_freezes_timer(self):
        mode = BattleMode(assets())
        notice = ConstraintNotice()
        notice.active.add('battle_rhythm')
        mode.framework = SimpleNamespace(notice=notice)
        with patch('codes.battle.get_time', return_value=0):
            mode.enter(False)
            remaining = mode.rules.remaining
            press(mode, SDLK_LEFT)
        self.assertEqual(mode.rules.health, 3)
        self.assertEqual(mode.rules.remaining, remaining)
        mode.update(.5)
        self.assertEqual(mode.rules.idle_remaining(.5), remaining)

    def test_claps_match_demo_and_input_for_every_pattern(self):
        rhythm = Rhythm(0)
        for segment in range(10):
            rhythm.segment, rhythm.started, rhythm.index = segment, segment * 4, 0
            rhythm.last_clap = rhythm.started - .001
            sound = Mock()
            for beat in rhythm.beat_times(False):
                rhythm.play_claps(beat, sound)
                rhythm.play_claps(beat, sound)
            self.assertEqual(sound.play.call_count, len(rhythm.hits))
            for index, beat in enumerate(rhythm.beat_times()):
                self.assertEqual(rhythm.advance(beat), 0)
                rhythm.play_claps(beat, sound)
                self.assertEqual(sound.play.call_count, len(rhythm.hits) + index + 1)
                self.assertEqual(rhythm.frame(beat), (0, 1))
                self.assertTrue(rhythm.press(beat))
                rhythm.play_claps(beat, sound)
                self.assertEqual(sound.play.call_count, len(rhythm.hits) + index + 1)

    def test_claps_do_not_burst_after_a_delayed_frame(self):
        rhythm, sound = Rhythm(0), Mock()
        rhythm.advance(4.4)
        rhythm.play_claps(4.4, sound)
        sound.play.assert_not_called()
        rhythm.play_claps(4.5, sound)
        sound.play.assert_called_once_with()

    def test_first_pattern_cue_is_once_and_leaves_room_before_the_second(self):
        rhythm = Rhythm(0)
        rhythm.patterns = [[1937.5], [0]]
        now = rhythm.beat_times()[0]
        self.assertFalse(rhythm.take_next_pattern_cue(now))
        self.assertTrue(rhythm.press(now))
        self.assertTrue(rhythm.take_next_pattern_cue(now))
        self.assertAlmostEqual(rhythm.next_start, now + rhythm.CUE_GAP)
        self.assertFalse(rhythm.take_next_pattern_cue(now))

    def test_countdown_places_go_sound_only_in_its_own_step(self):
        countdown, sound = RhythmCountdown(0), Mock()
        for index, label in enumerate(('3', '2', '1', 'GO')):
            tick = index * countdown.STEP
            self.assertEqual(countdown.frame(tick), (label, 1))
            countdown.play_go(tick, sound)
            countdown.play_go(tick + .1, sound)
            self.assertEqual(sound.play.call_count, int(label == 'GO'))

    def test_input_clap_accepts_action_without_a_second_sound(self):
        mode = BattleMode(assets())
        mode.assets.clap_sound = Mock()
        notice = ConstraintNotice()
        notice.active.add('battle_rhythm')
        mode.framework = SimpleNamespace(notice=notice)
        with patch('codes.battle.get_time', return_value=0):
            mode.enter(False)
        now = mode.rhythm.beat_times()[0]
        with patch('codes.battle.get_time', return_value=now):
            mode.update(now)
            mode.assets.clap_sound.play.assert_called_once_with()
            press(mode, SDLK_LEFT)
        self.assertEqual(mode.successes, 1)
        self.assertEqual(mode.rules.health, 3)
        mode.assets.clap_sound.play.assert_called_once_with()

    def test_last_beat_accepts_late_input_across_segment_boundary(self):
        rhythm = Rhythm(0)
        rhythm.segment = 8
        rhythm.index = len(rhythm.hits) - 1
        now = rhythm.beat_times()[-1] + .099
        self.assertEqual(rhythm.advance(now), 0)
        self.assertTrue(rhythm.press(now))
        rhythm.advance(now)
        self.assertEqual(rhythm.segment, 9)
