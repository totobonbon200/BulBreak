# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""주인공 주변 원 바깥의 미로를 검은색으로 가린다."""
from math import sqrt
from pico2d import draw_line

def draw_darkness(x, y, radius):
    for row in range(100, 501):
        half = sqrt(max(0, radius ** 2 - (row - y) ** 2))
        draw_line(100, row, max(100, x - half), row, 0, 0, 0)
        draw_line(min(500, x + half), row, 500, row, 0, 0, 0)
