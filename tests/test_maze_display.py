import unittest
from unittest.mock import Mock, patch
from codes.maze import Maze


class MazeDisplayTests(unittest.TestCase):
    def test_four_by_four_is_rejected(self):
        with self.assertRaises(ValueError):
            Maze(4)

    def test_six_by_six_grid_and_wall_numbers_are_white_without_labels(self):
        maze = Maze(6)
        font = Mock()
        with patch('pico2d.draw_rectangle') as grid:
            maze.draw(Mock(w=800, h=400), font)
        self.assertEqual(grid.call_count, 36)
        self.assertTrue(all(c.args[-3:] == (255, 255, 255) for c in grid.call_args_list))
        self.assertEqual(len(font.draw.call_args_list), len(maze.walls))
        self.assertTrue(all(c.args[2] == '2' and c.args[3] == (255, 255, 255)
                            for c in font.draw.call_args_list))
