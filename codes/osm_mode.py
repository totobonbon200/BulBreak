"""중앙의 주인공을 향해 날아오는 노트를 맞히는 디버그 제약."""
# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_DOWN, SDLK_LEFT, SDLK_RIGHT, SDLK_UP
from pico2d import draw_line, draw_rectangle
from codes.hud import info_text
from codes.menu_modes import MenuMode


class OsmMode(MenuMode):
    CENTER = (300, 300)
