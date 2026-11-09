"""Player state and the top-row maze animation."""

from enum import Enum, auto
from codes.gameover import GameOverRules


class PlayerState(Enum):
    PLAYING = auto()
    GAME_OVER = auto()


class Character:
    IDLE_TIMEOUT = 3.0

    def __init__(self, position, now=0.0):
        self.position = position
        self.animation_until = 0.0
        self.state = PlayerState.PLAYING
        self.rules = GameOverRules(now)

    @property
    def is_playing(self):
        return self.state is PlayerState.PLAYING

    def idle_remaining(self, now):
        return self.rules.idle_remaining(now)

    def update(self, now):
        self.rules.update(now)
        if self.is_playing and self.rules.is_over:
            self.state = PlayerState.GAME_OVER

    def enter_maze(self, position, now):
        # Scene transitions do not consume idle time.
        self.position = position
        self.rules.enter_maze(now)

    def react(self, now):
        if not self.is_playing:
            return
        self.rules.record_action(now)
        self.animation_until = now + 0.15

    def draw(self, sheet, maze, now):
        width, height = sheet.w // 4, sheet.h // 4
        frame = int(now < self.animation_until)
        x, y = maze.center(self.position)
        size = maze.cell_size * .7
        sheet.clip_draw(frame * width, 3 * height, width, height,
                        x, y, size, size)
