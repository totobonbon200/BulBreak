# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""봄버맨 미로에서 폭탄 세 개의 위치와 판정 시각을 관리한다."""
from random import sample

class BomberRound:
    def __init__(self, maze, now):
        self.deadline = now + 2.0
        passages = [(row, col) for row in range(maze.size) for col in range(maze.size)
                    if (row, col) not in maze.walls]
        self.bombs = sample(passages, 3)
