"""미로 모드의 입력, 진행, 표시를 연결한다."""
import random
from pico2d import *

from codes.maze import Maze
from codes.character import Character


class MazeMode:
    def __init__(self, assets):
        self.assets = assets
        self.held = set()
        self.size = random.choice((4, 6))
        self.completed = 0
        self.maze = Maze(self.size)
        self.player = Character(self.maze.entrance, get_time())
        self.now = get_time()
        self.message = 'Arrow keys: move / hit wall twice'
        self.transitioned = False

    def enter(self, first_visit):
        self.held.clear()
        self.player.enter_maze(self.player.position, get_time())

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
            if not self.player.is_playing or self.transitioned:
                return
            self.player.position, result = self.maze.step(
                self.player.position, directions[event.key])
            self.player.react(self.now)
            self.message = {'hit': 'Wall: 1 hit left',
                            'broken': 'Wall broken! Press again to move.',
                            'blocked': 'Map boundary',
                            'moved': 'Arrow keys: move / hit wall twice',
                            'exit': 'Next maze'}[result]
            if result == 'exit':
                self.completed += 1
                self.maze = Maze(self.size, self.maze.exit)
                self.player.enter_maze(self.maze.entrance, self.now)
                self.transitioned = True

    def update(self, now):
        self.now = now
        self.transitioned = False
        self.player.update(now)

    def draw(self):
        sheet, font = self.assets.maze_sheet, self.assets.font
        self.maze.draw(sheet, font, self.now)
        self.player.draw(self.assets.character_sheet, self.maze, self.now)
        font.draw(100, 550, f'BulBreak | {self.size}x{self.size} | Maze {self.completed + 1} | {self.player.state.name}', (20, 20, 20))
        if self.player.is_playing:
            font.draw(100, 525, f'Idle time left: {self.player.idle_remaining(self.now):.1f}s', (180, 40, 40))
            font.draw(550, 550, f'HP: {self.player.rules.health}', (180, 40, 40))
        else:
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
