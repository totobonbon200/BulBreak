# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md의 최신 기준을 확인한다.
"""미로 모드의 입력, 진행, 표시를 연결한다."""
from pico2d import *

from codes.maze import Maze
from codes.maze_darkness import draw_darkness
from codes.clap_sound import play_go_sound
from codes.cross_maze import CrossMaze
from codes.hud import draw_hud
from codes.character import Character


class MazeMode:
    def __init__(self, assets):
        self.assets = assets
        self.pending_session = None
        self.held = set()
        self.reset(get_time())

    def reset(self, now):
        self.size = 6
        self.completed = 0
        self.score = 0
        self.cross_count = 0  # 한 미로에서 출구 방향 선택 여섯 번을 센다.
        notice = getattr(getattr(self, 'framework', None), 'notice', None)
        self.cross_enabled = notice is not None and isinstance(notice.active, set) and 'maze_cross' in notice.active
        self.darkness = notice is not None and isinstance(notice.active, set) and 'maze_darkness' in notice.active
        self.maze = CrossMaze() if self.cross_enabled else Maze(self.size)
        self.player = Character(self.maze.entrance, now)
        self.now = now
        self.message = '방향키: 이동 / 벽은 두 번 공격'
        self.transitioned = False

    @property
    def is_game_over(self):
        return not self.player.is_playing

    def enter(self, first_visit):
        self.held.clear()
        self.reset(get_time())
        if self.pending_session is not None:
            self.player.rules, self.score = self.pending_session
            self.pending_session = None
            self.player.rules.enter_maze(self.now)

    def exit(self):
        self.held.clear()

    def handle_event(self, event):
        directions = {SDLK_UP: (-1, 0), SDLK_DOWN: (1, 0),
                      SDLK_LEFT: (0, -1), SDLK_RIGHT: (0, 1)}
        if event.type == SDL_KEYUP:
            self.held.discard(event.key)
        elif event.type == SDL_KEYDOWN and event.key in directions:
            if getattr(event, 'repeat', False):
                return
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
            self.message = {'hit': '벽: 한 번 더 공격',
                            'broken': '벽 파괴 완료! 다시 누르면 이동',
                            'blocked': '미로의 경계입니다',
                            'moved': '방향키: 이동 / 벽은 두 번 공격',
                            'exit': '다음 미로'}[result]
            if result == 'exit':
                play_go_sound(self.assets)
                if self.cross_enabled:
                    self.cross_count += 1
                    if self.cross_count < 6:
                        self.maze.choose_exit()
                        self.player.position = self.maze.entrance
                        self.message = f'출구 방향 선택: {self.cross_count}/6'
                        return
                self.completed += 1
                if self.completed == 2:
                    battle = self.framework.modes['battle_mode']
                    battle.pending_session = (self.player.rules, self.score)
                    self.framework.change_mode('battle_mode')
                    return
                self.advance_maze()

    def complete_maze(self):
        # 실제 출구와 폭탄 회피가 같은 미로 완료 흐름을 사용한다.
        self.completed += 1
        if self.completed == 2:
            battle = self.framework.modes['battle_mode']
            battle.pending_session = (self.player.rules, self.score)
            self.framework.change_mode('battle_mode')
            return
        self.advance_maze()

    def advance_maze(self):
        # 디버그 한 판은 출구에 도착하면 선택 목록으로 돌아간다.
        if getattr(self.framework, 'practicing_constraint', False) is True:
            self.framework.change_mode('instrument_mode')
            return
        # 일반 진행에서는 직전 출구에서 다음 미로를 시작한다.
        self.now = get_time()
        self.cross_count = 0
        self.maze = CrossMaze() if self.cross_enabled else Maze(self.size, self.maze.exit)
        self.player.enter_maze(self.maze.entrance, self.now)
        self.message = '방향키: 이동 / 벽은 두 번 공격'
        self.transitioned = True

    def update(self, now):
        self.now = now
        self.transitioned = False
        self.player.update(now)

    def draw(self):
        sheet, font = self.assets.maze_sheet, self.assets.font
        self.maze.draw(sheet, font, self.now)
        self.player.draw(self.assets.character_sheet, self.maze, self.now)
        if self.darkness:
            draw_darkness(*self.maze.center(self.player.position), self.maze.cell_size * 1.5)
        framework = getattr(self, 'framework', None)
        paused = self.is_game_over or getattr(framework, 'timer_paused', False) is True
        draw_hud(self.assets, self.player.rules, self.now, self.completed, timer_paused=paused)
        if not self.player.is_playing:
            width, height = sheet.w // 4, sheet.h // 2
            sheet.opacify(0.5)
            try:
                sheet.clip_draw(3 * width, height, width, height,
                                400, 300, 800, 600)
            finally:
                sheet.opacify(1.0)
