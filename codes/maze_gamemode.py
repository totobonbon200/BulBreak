"""미로 모드의 입력, 진행, 표시를 연결한다."""
import random
from pico2d import *

from codes.maze import Maze
from codes.character import Character, PlayerState


class MazeMode:
    def __init__(self, assets):
        self.assets = assets
        self.held = set()
        self.reset(get_time())

    def reset(self, now):
        self.stage_timed_out = False
        self.size = random.choice((4, 6))
        self.completed = 0
        self.maze = Maze(self.size)
        self.player = Character(self.maze.entrance, now)
        self.now = now
        self.message = 'Arrow keys: move / hit wall twice'
        self.transitioned = False
        framework = getattr(self, 'framework', None)
        if framework is not None:
            framework.restart_stage_timer()

    @property
    def use_stage_deadline(self):
        return self.player.rules.rule == 3

    @property
    def is_game_over(self):
        return not self.player.is_playing

    def on_stage_timeout(self):
        self.stage_timed_out = True
        self.player.state = PlayerState.GAME_OVER
        self.message = ''

    def enter(self, first_visit):
        self.held.clear()
        self.reset(get_time())

    def exit(self):
        self.held.clear()

    def handle_event(self, event):
        directions = {SDLK_UP: (-1, 0), SDLK_DOWN: (1, 0),
                      SDLK_LEFT: (0, -1), SDLK_RIGHT: (0, 1)}
        if event.type == SDL_KEYUP:
            self.held.discard(event.key)
        elif event.type == SDL_KEYDOWN and event.key in directions:
            if event.key in self.held:
                return
            self.held.add(event.key)
            if not self.player.is_playing:
                if event.key == SDLK_DOWN:
                    self.reset(get_time())
                    self.transitioned = True
                elif event.key == SDLK_UP:
                    self.framework.change_mode('start_mode')
                return
            if self.transitioned:
                return
            self.player.position, result = self.maze.step(
                self.player.position, directions[event.key])
            self.player.react(self.now, result, directions[event.key])
            self.message = {'hit': 'Wall: 1 hit left',
                            'broken': 'Wall broken! Press again to move.',
                            'blocked': 'Map boundary',
                            'moved': 'Arrow keys: move / hit wall twice',
                            'exit': 'Next maze'}[result]
            if result == 'exit':
                self.completed += 1
                self.maze = Maze(self.size, self.maze.exit)
                self.player.enter_maze(self.maze.entrance, self.now)
                self.framework.restart_stage_timer()
                self.transitioned = True

    def update(self, now):
        self.now = now
        self.transitioned = False
        self.player.update(now)

    def draw(self):
        sheet, font = self.assets.maze_sheet, self.assets.font
        self.maze.draw(sheet, font, self.now)
        self.player.draw(self.assets.character_sheet, self.maze, self.now)
        rule = self.player.rules.rule
        label = {1: '무행동 3초 / 입력 시 1초 회복', 2: '체력 3개 / 3초마다 1 감소', 3: '15초 제한'}[rule]
        font.draw(100, 575, f'게임오버 기준 {rule}번: {label}', (255, 255, 255))
        font.draw(100, 550, f'BulBreak | {self.size}x{self.size} | Maze {self.completed + 1}', (255, 255, 255))
        if self.player.is_playing:
            status = (f'남은 시간: {self.player.idle_remaining(self.now):.1f}초' if rule == 1
                      else f'체력: {self.player.rules.health} / 3')
            font.draw(100, 525, status, (255, 220, 100))
        elif not self.stage_timed_out:
            self.message = 'GAME OVER: time or health depleted'
        font.draw(100, 70, self.message, (20, 20, 20))
        font.draw(100, 45, 'IN: entrance / OUT: exit | Close window to quit', (20, 20, 20))
        if not self.player.is_playing:
            width, height = sheet.w // 4, sheet.h // 2
            sheet.opacify(0.5)
            try:
                sheet.clip_draw(3 * width, height, width, height,
                                400, 300, 800, 600)
            finally:
                sheet.opacify(1.0)
            font.draw(180, 320, 'DOWN: restart / UP: start screen', (220, 40, 40))
