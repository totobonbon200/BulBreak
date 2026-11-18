# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""첫 게임에서 미로·전투·제약을 직접 익히는 튜토리얼."""
from collections import deque
from pico2d import (SDL_KEYDOWN, SDL_KEYUP, SDLK_DOWN, SDLK_LEFT, SDLK_RIGHT, SDLK_UP,
                    draw_rectangle, get_canvas_height, get_canvas_width)
from codes.hud import info_text
