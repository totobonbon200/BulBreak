# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""봄버맨 미로에서 폭탄 세 개의 위치와 판정 시각을 관리한다."""
from random import choice, sample
from pico2d import draw_rectangle
from codes.animation import draw_frame
from codes.hud import info_text

def choose_spawn(maze):
    # 입구와 도착점을 제외한 통로에서 주인공의 시작 위치를 고른다.
    excluded = {maze.entrance, maze.exit} | maze.walls.keys()
    passages = [(row, col) for row in range(maze.size) for col in range(maze.size)
                if (row, col) not in excluded]
    return choice(passages)


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

    def draw(self, maze, assets, now):
        # 폭탄 표시에는 effect 시트의 첫 행 세 번째 칸을 사용한다.
        self.draw_blast(maze)
        size = maze.cell_size * .8
        for bomb in self.bombs:
            draw_frame(assets.effect_sheet, 2, 4, (0, 2), *maze.center(bomb), size, size)
        info_text(assets.font, 108, 78, f'폭발까지 {max(0, self.deadline - now):.1f}초')
