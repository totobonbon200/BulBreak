# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""중앙에서 출구를 고르는 다섯 칸 제약 미로."""
import random
from codes.maze import Maze


class CrossMaze(Maze):
    def __init__(self):
        self.size, self.entrance = 3, (1, 1)
        self.choose_exit()

    def choose_exit(self):
        # 모서리는 표시하지 않고 인접 네 칸 중 출구 하나만 연다.
        self.neighbors = [(0, 1), (2, 1), (1, 0), (1, 2)]
        self.exit = random.choice(self.neighbors)
        self.walls = {cell: 2 for cell in self.neighbors if cell != self.exit}

    def step(self, position, direction):
        target = tuple(a + b for a, b in zip(self.entrance, direction))
        return (target, 'exit') if target == self.exit else (self.entrance, 'blocked')
