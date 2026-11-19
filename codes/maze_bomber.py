# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""봄버맨 미로에서 폭탄 세 개의 위치와 판정 시각을 관리한다."""
from random import choice, sample

class BomberRound:
    def __init__(self, maze, position, now):
        self.deadline = now + 2.0
        safe_row, safe_col = self.nearby_shelter(maze, position)
        passages = [(row, col) for row in range(maze.size) if row != safe_row
                    for col in range(maze.size) if col != safe_col and (row, col) not in maze.walls]
        self.bombs = sample(passages, 3)

    def nearby_shelter(self, maze, position):
        # 한 번 움직여 갈 수 있는 통로를 우선 대피 칸으로 고른다.
        row, col = position
        neighbors = ((row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1))
        passages = [cell for cell in neighbors if all(0 <= axis < maze.size for axis in cell)
                    and cell not in maze.walls]
        return choice(passages or [position])
