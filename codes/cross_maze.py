# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""중앙에서 출구를 고르는 다섯 칸 제약 미로."""
import random
from codes.maze import Maze


class CrossMaze(Maze):
    def __init__(self):
        self.size, self.entrance = 3, (1, 1)
        self.choose_exit()
