# 여기에다 게임 메인루프 만들고 BulBreak.py에는 canvas.open, close의 기능만을 사용하고 나머지는 클래스, 함수의 구성으로만 작성
"""게임 자원과 메인 루프."""
# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
from pathlib import Path
# 이걸로 상태머신 표현할 것: from transitions import *
from pico2d import * # pico2d는 이걸로 불러올 것
from sdl2 import (SDL_SetHint, SDL_HINT_RENDER_SCALE_QUALITY,
                  SDL_SetRenderDrawBlendMode, SDL_BLENDMODE_BLEND)

from codes.maze_gamemode import MazeMode
from codes.battle import BattleMode
from codes.cat_constraint import CatEffect
from codes.clap_sound import load_clap
from codes.game_framework import GameFramework
from codes.menu_modes import create_menus


class Assets:
    def __init__(self):
        SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, b'linear')
        SDL_SetRenderDrawBlendMode(draw_rectangle.__globals__['renderer'], SDL_BLENDMODE_BLEND)
        # 시범과 정확한 입력이 같은 박수 효과음을 공유한다.
        self.clap_sound = load_clap()
        root = Path(__file__).resolve().parents[1]
        self.main_image = load_image(str(root / 'resources/Main.png'))  # 시작 화면 로고
        self.menu_image = load_image(str(root / 'resources/Menu.png'))  # 시작·게임 공용 패널
        self.maze_sheet = load_image(str(root / 'resources/maze_800x400.png'))
        self.character_sheet = load_image(str(root / 'resources/character_600x600.png'))
        self.character_attack_sheet = load_image(str(root / 'resources/character_attacks_800x400.png'))
        self.effect_sheet = load_image(str(root / 'resources/effect_800x400.png'))
        self.yellow_arrow_sheet = load_image(str(root / 'resources/effect_arrows_yellow.png'))
        self.effect_attack_sheet = load_image(str(root / 'resources/effect_attack_800x200.png'))
        self.enemy_sheet = load_image(str(root / 'resources/enemy_animation_600x600.png'))
        self.result_sheet = load_image(str(root / 'resources/result_800x400.png'))
        font_path = root / 'resources/esamanru-Medium.ttf'
        if not font_path.is_file():
            raise FileNotFoundError('README.md의 실행 글꼴 안내에 따라 이사만루체를 설치하세요.')
        self.font = load_font(str(font_path), 15)
        self.notice_font = load_font(str(font_path), 24)
        self.timeout_font = load_font(str(font_path), 38)
        # 미로와 전투가 같은 고양이 자원과 캔버스 경계를 사용한다.
        self.cat_effect = CatEffect(
            load_image(str(root / 'resources/manja-vitolic-gKXKBY-C-Dk-unsplash.jpg')),
            load_image(str(root / 'resources/cat_yawn.png')),
            get_canvas_width(), get_canvas_height())


def main():
    assets = Assets()
    modes = create_menus(assets.font, assets.main_image, assets.menu_image,
                         start_font=assets.notice_font)
    modes['maze_mode'] = MazeMode(assets)
    modes['battle_mode'] = BattleMode(assets)
    framework = GameFramework(modes, timeout_font=assets.timeout_font,
                              cat_effect=assets.cat_effect)
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
