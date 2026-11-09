"""방향키로 이동하는 시작 및 안내 화면."""
from pico2d import *


class MenuMode:
    def __init__(self, font, title, lines, routes):
        self.font = font
        self.title = title
        self.lines = lines
        self.routes = routes
        self.framework = None
        self.held = set()

    def enter(self, first_visit):
        self.held.clear()

    def exit(self):
        self.held.clear()

    def handle_event(self, event):
        if event.type == SDL_KEYUP:
            self.held.discard(event.key)
        elif event.type == SDL_KEYDOWN and event.key in self.routes:
            if event.key not in self.held:
                self.held.add(event.key)
                self.framework.change_mode(self.routes[event.key])

    def update(self, now):
        pass

    def draw(self):
        self.font.draw(100, 500, self.title, (20, 20, 20))
        for index, line in enumerate(self.lines):
            self.font.draw(100, 450 - 30 * index, line, (20, 20, 20))


def create_menus(font):
    return {
        'start_mode': MenuMode(font, 'BulBreak',
                              ['RIGHT: start maze', 'UP: instructions', 'LEFT: quit'],
                              {SDLK_RIGHT: 'maze_mode', SDLK_UP: 'instrument_mode',
                               SDLK_LEFT: 'quit_mode'}),
        'instrument_mode': MenuMode(font, 'Instructions',
                                   ['Arrow keys: move / hit wall',
                                    'Hit a wall twice, then move into it.',
                                    'Reach OUT to enter the next maze.',
                                    'LEFT: back'], {SDLK_LEFT: 'start_mode'}),
        'battle_mode': MenuMode(font, 'Battle: planned',
                               ['Combat is not implemented yet.', 'LEFT: back'],
                               {SDLK_LEFT: 'start_mode'}),
        'result_mode': MenuMode(font, 'Results: planned',
                               ['Scoring is not implemented yet.', 'LEFT: back'],
                               {SDLK_LEFT: 'start_mode'}),
    }
