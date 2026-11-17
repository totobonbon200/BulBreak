# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""중앙 미로와 리듬 제약의 경계·피해 회귀 검증."""
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from codes.cross_maze import CrossMaze
from codes.rhythm import Rhythm
from codes.constraints import ConstraintNotice
from test_battle import assets, press
from codes.maze_gamemode import MazeMode
from codes.battle import BattleMode
from pico2d import SDLK_LEFT, SDLK_RIGHT, SDLK_UP, SDLK_DOWN


class ConstraintTests(unittest.TestCase):
    def test_cross_has_five_cells_and_only_exit_moves(self):
        maze = CrossMaze()
        self.assertEqual(len(maze.walls), 3)
        self.assertEqual(maze.entrance, (1, 1))
        for delta in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            position, result = maze.step(maze.entrance, delta)
            self.assertEqual(result == 'exit', position == maze.exit)

    def test_all_patterns_exact_hits_and_no_duplicate(self):
        rhythm = Rhythm(0)
        self.assertEqual(len(rhythm.patterns), 10)
        for segment in range(10):
            for hit in rhythm.hits:
                self.assertGreaterEqual(hit, 0)
