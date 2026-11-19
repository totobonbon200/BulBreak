# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""주인공 주변 원 바깥의 미로를 검은색으로 가린다."""
from math import sqrt
from pico2d import draw_line

def exit_hint_opacity(exit_cell, position):
    # 두 축 중 먼 쪽을 기준으로 3×3과 5×5를 나눈다.
    distance = max(abs(cell - origin) for cell, origin in zip(exit_cell, position))
    return (.35, .35, .12)[distance] if distance <= 2 else 0.0

def draw_darkness(x, y, radius):
    for row in range(100, 501):
        half = sqrt(max(0, radius ** 2 - (row - y) ** 2))
        draw_line(100, row, max(100, x - half), row, 0, 0, 0)
        draw_line(min(500, x + half), row, 500, row, 0, 0, 0)
