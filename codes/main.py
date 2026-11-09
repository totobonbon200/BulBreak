"""게임 자원과 메인 루프."""
from pathlib import Path
from pico2d import *

from codes.maze_gamemode import MazeMode
from codes.game_framework import GameFramework
from codes.menu_modes import create_menus


class Assets:
    def __init__(self):
        root = Path(__file__).resolve().parents[1]
        self.maze_sheet = load_image(str(root / 'resources/maze_animation_sheet.png'))
        self.character_sheet = load_image(str(root / 'resources/character_animation_sheet.png'))
        self.font = load_font('C:/Windows/Fonts/arial.ttf', 15)


def main():
    assets = Assets()
    modes = create_menus(assets.font)
    modes['maze_mode'] = MazeMode(assets)
    framework = GameFramework(modes)
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
        framework.draw()
        update_canvas()
        delay(0.01)
