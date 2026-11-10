"""A separate guide screen describing the playable maze prototype."""
from pico2d import SDL_KEYDOWN, SDLK_RIGHT


class GuideMode:
    def __init__(self, font):
        self.font = font
        self.framework = None

    def enter(self, first_visit):
        pass

    def exit(self):
        pass

    def update(self, now):
        pass

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_RIGHT:
            self.framework.change_mode('start_mode')

    def draw(self):
        self.font.draw(70, 540, 'BulBreak - Guide', (255, 255, 255))
        sections = (
            ('MOVE & ESCAPE', (
                'Tap arrow keys to move. Reach OUT to enter the next maze.',
                'Hit a wall twice to break it, then press again to move in.',
                'Release each key before pressing again; holding is not a new action.')),
            ('KEEP MOVING', (
                'Idle time starts at 3 seconds. Each press restores 1 second (max 3).',
                'You start with 3 HP. Every 3 seconds in a maze costs 1 HP.',
                'Reaching OUT restarts the HP countdown, but does not refill HP.',
                'Zero idle time or zero HP means GAME OVER.')),
            ('STAGE DEADLINE', (
                'Each maze or battle has a separate 15-second limit.',
                'Inputs cannot extend it. At 15 seconds, the run ends.',)),
            ('CURRENT VERSION', (
                'Mazes repeat. Combat and constraint gameplay are not available yet.',)),
        )
        y = 490
        for title, lines in sections:
            self.font.draw(70, y, title, (255, 220, 100))
            y -= 28
            for line in lines:
                self.font.draw(70, y, line, (255, 255, 255))
                y -= 26
            y -= 18
        self.font.draw(70, 45, 'RIGHT: return to start', (255, 220, 100))
