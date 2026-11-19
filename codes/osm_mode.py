"""중앙의 주인공을 향해 날아오는 노트를 맞히는 디버그 제약."""
# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_DOWN, SDLK_LEFT, SDLK_RIGHT, SDLK_UP
from pico2d import draw_line, draw_rectangle
from codes.hud import info_text
from codes.menu_modes import MenuMode


class OsmMode(MenuMode):
    CENTER = (300, 300)
    TRAVEL = 1.0
    WINDOW = 0.15
    RADIUS = 180
    # 입력 방향은 노트가 주인공을 향해 이동하는 방향이다.
    DIRECTIONS = {SDLK_UP: (0, 1), SDLK_DOWN: (0, -1),
                  SDLK_LEFT: (-1, 0), SDLK_RIGHT: (1, 0)}
    PATTERN = (SDLK_RIGHT, SDLK_DOWN, SDLK_LEFT, SDLK_UP,
               SDLK_LEFT, SDLK_DOWN, SDLK_RIGHT, SDLK_UP)
