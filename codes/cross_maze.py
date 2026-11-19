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

    def draw(self, sheet, font, now=0.0, *, show_exit=True):
        # 십자형 다섯 칸만 기존 미로 자원으로 표시한다.
        width, height = sheet.w // 4, sheet.h // 2
        for cell in [self.entrance] + self.neighbors:
            x, y = self.center(cell)
            sheet.clip_draw(0 if show_exit and cell == self.exit else width, height,
                            width, height, x, y, self.cell_size, self.cell_size)
            if cell in self.walls:
                sheet.clip_draw(0, 0, width, height, x, y, self.cell_size * .55, self.cell_size * .55)
