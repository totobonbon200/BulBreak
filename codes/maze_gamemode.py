"""미로 모드의 입력, 진행, 표시를 연결한다."""
from pico2d import *

from codes.maze import Maze
from codes.hud import draw_hud, text
from codes.character import Character, PlayerState


class MazeMode:
    def __init__(self, assets):
        self.assets = assets
        self.held = set()
        self.reset(get_time())

    def reset(self, now):
        self.stage_timed_out = False
        self.size = 6
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
        draw_hud(self.assets, self.player.rules, self.now, self.completed)
        if not self.player.is_playing and not self.stage_timed_out:
            self.message = '체력이 모두 소진되었습니다'
        text(font, 100, 70, self.message)
        text(font, 100, 45, '방향키: 이동·벽 공격 / 입구 IN · 출구 OUT')
        if not self.player.is_playing:
            width, height = sheet.w // 4, sheet.h // 2
            sheet.opacify(0.5)
            try:
                sheet.clip_draw(3 * width, height, width, height,
                                400, 300, 800, 600)
            finally:
                sheet.opacify(1.0)
            text(font, 180, 320, '아래: 재시작 / 위: 시작 화면')
