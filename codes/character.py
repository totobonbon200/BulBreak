"""Player state and the top-row maze animation."""

from enum import Enum, auto
from transitions import Machine
from codes.gameover import GameOverRules


class PlayerState(Enum):
    PLAYING = auto()
    GAME_OVER = auto()


class Character:
    IDLE_TIMEOUT = 3.0
    FRAME_SECONDS = 0.15
    WALL_ATTACK_DISTANCE = 0.2

    def __init__(self, position, now=0.0):
        self.position = position
        self.animation_until = 0.0
        self.animation_started = now
        self.attack_direction = (0, 0)
        self.flip_horizontal = False
        self.action_machine = Machine(
            model=self, states=['idle', 'moving', 'wall_attack'], initial='idle',
            model_attribute='action_state', auto_transitions=False)
        self.action_machine.add_transition('start_move', '*', 'moving')
        self.action_machine.add_transition('start_wall_attack', '*', 'wall_attack')
        self.action_machine.add_transition('finish_action', '*', 'idle')
        self.state = PlayerState.PLAYING
        self.rules = GameOverRules(now)

    @property
    def is_playing(self):
        return self.state is PlayerState.PLAYING

    def idle_remaining(self, now):
        return self.rules.idle_remaining(now)

    def update(self, now):
        self.rules.update(now)
        if now >= self.animation_until:
            self.finish_action()
        if self.is_playing and self.rules.is_over:
            self.state = PlayerState.GAME_OVER

    def enter_maze(self, position, now):
        # Scene transitions do not consume idle time.
        self.position = position
        self.rules.enter_maze(now)
        self.finish_action()

    def react(self, now, result='moved', direction=(0, 0)):
        if not self.is_playing:
            return
        self.flip_horizontal = direction == (0, -1)
        self.rules.record_action(now)
        if result in ('moved', 'exit'):
            self.start_move()
        elif result in ('hit', 'broken'):
            self.attack_direction = direction
            self.start_wall_attack()
        else:
            return
        if self.action_state != 'idle':
            self.animation_started = now
            self.animation_until = now + 2 * self.FRAME_SECONDS

    def draw(self, sheet, maze, now):
        width, height = sheet.w // 4, sheet.h // 4
        frame = 0
        if self.action_state != 'idle':
            frame = min(1, int(max(0, now - self.animation_started) / self.FRAME_SECONDS))
        x, y = maze.center(self.position)
        if self.action_state == 'wall_attack':
            progress = min(1.0, max(0.0, now - self.animation_started)
                           / (2 * self.FRAME_SECONDS))
            frame = 1 if progress < 0.5 else 0
            offset = (1 - abs(2 * progress - 1)) * maze.cell_size * self.WALL_ATTACK_DISTANCE
            row, column = self.attack_direction
            x += column * offset
            y -= row * offset
        size = maze.cell_size * .8
        flip = 'h' if self.flip_horizontal else ''
        sheet.clip_composite_draw(frame * width, 3 * height, width, height,
                                  0, flip, x, y, size, size)
