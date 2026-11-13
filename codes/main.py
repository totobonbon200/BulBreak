# 여기에다 게임 메인루프 만들고 BulBreak.py에는 canvas.open, close의 기능만을 사용하고 나머지는 클래스, 함수의 구성으로만 작성
"""게임 자원과 메인 루프."""
from pathlib import Path
# 이걸로 상태머신 표현할 것: from transitions import *
from pico2d import * # pico2d는 이걸로 불러올 것
from sdl2 import (SDL_SetHint, SDL_HINT_RENDER_SCALE_QUALITY,
                  SDL_SetRenderDrawBlendMode, SDL_BLENDMODE_BLEND)

from codes.maze_gamemode import MazeMode
from codes.game_framework import GameFramework
from codes.menu_modes import create_menus


class Assets:
    def __init__(self):
        SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, b'linear')
        SDL_SetRenderDrawBlendMode(draw_rectangle.__globals__['renderer'], SDL_BLENDMODE_BLEND)
        root = Path(__file__).resolve().parents[1]
        self.maze_sheet = load_image(str(root / 'resources/maze_800x400.png'))
        self.character_sheet = load_image(str(root / 'resources/character_600x600.png'))
        self.character_attack_sheet = load_image(str(root / 'resources/character_attacks_800x400.png'))
        self.effect_sheet = load_image(str(root / 'resources/effect_800x400.png'))
        self.result_sheet = load_image(str(root / 'resources/result_800x400.png'))
        self.font = load_font('C:/Windows/Fonts/malgun.ttf', 15)
        self.timeout_font = load_font('C:/Windows/Fonts/malgun.ttf', 38)


def main():
    assets = Assets()
    modes = create_menus(assets.font)
    modes['maze_mode'] = MazeMode(assets)
    framework = GameFramework(modes, timeout_font=assets.timeout_font)
    for mode in modes.values():
        mode.framework = framework
    while framework.running:
        framework.update(get_time())
        for event in get_events():
            if event.type == SDL_QUIT:
                framework.change_mode('quit_mode')
                break
            previous = framework.current_mode
            framework.handle_event(event)
            if framework.current_mode != previous:
                break
        if not framework.running:
            break
        clear_canvas()
        draw_rectangle(0, 0, 799, 599, 0, 0, 0, 255, filled=True)
        framework.draw()
        update_canvas()
        delay(0.01)
