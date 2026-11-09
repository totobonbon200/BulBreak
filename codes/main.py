"""게임 자원과 메인 루프."""
from pathlib import Path
from pico2d import *

from codes.maze_gamemode import MazeMode


class Assets:
    def __init__(self):
        root = Path(__file__).resolve().parents[1]
        self.maze_sheet = load_image(str(root / 'resources/maze_animation_sheet.png'))
        self.character_sheet = load_image(str(root / 'resources/character_animation_sheet.png'))
        self.font = load_font('C:/Windows/Fonts/arial.ttf', 15)


def main():
    mode = MazeMode(Assets())
    mode.enter(True)
    running = True
    while running:
        mode.update(get_time())
        for event in get_events():
            if event.type == SDL_QUIT:
                running = False
            else:
                mode.handle_event(event)
        clear_canvas()
        mode.draw()
        update_canvas()
        delay(0.01)
