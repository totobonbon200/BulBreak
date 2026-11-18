# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""첫 게임에서 미로·전투·제약을 직접 익히는 튜토리얼."""
from collections import deque
from pico2d import (SDL_KEYDOWN, SDL_KEYUP, SDLK_DOWN, SDLK_LEFT, SDLK_RIGHT, SDLK_UP,
                    draw_rectangle, get_canvas_height, get_canvas_width)
from codes.hud import info_text


def dim_outside(focus):
    # 강조 영역 주변의 네 구역에만 검은색 70%를 합성한다.
    left, bottom, right, top = focus
    width, height = get_canvas_width(), get_canvas_height()
    regions = ((0, 0, left, height), (right, 0, width, height),
               (left, 0, right, bottom), (left, top, right, height))
    for region in regions:
        draw_rectangle(*region, 0, 0, 0, 179, filled=True)
