# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""봄버맨 미로에서 폭탄 세 개의 위치와 판정 시각을 관리한다."""
from random import choice, sample
from pico2d import draw_rectangle

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

    def in_blast(self, position):
        # 십자는 벽에 막히지 않고 미로 끝까지 이어진다.
        row, col = position
        return any(row == bomb_row or col == bomb_col for bomb_row, bomb_col in self.bombs)

    def draw_blast(self, maze):
        # 교차한 곳도 한 번만 칠해 폭발 범위를 같은 밝기로 보여준다.
        half = maze.cell_size / 2
        for row in range(maze.size):
            for col in range(maze.size):
                if self.in_blast((row, col)):
                    x, y = maze.center((row, col))
                    draw_rectangle(x - half, y - half, x + half, y + half, 240, 90, 25, 85, filled=True)
