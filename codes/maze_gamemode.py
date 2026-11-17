# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md의 최신 기준을 확인한다.
"""미로 모드의 입력, 진행, 표시를 연결한다."""
from pico2d import *

from codes.maze import Maze
from codes.cross_maze import CrossMaze
from codes.hud import draw_hud, info_text as text
from codes.character import Character, PlayerState


class MazeMode:
    def __init__(self, assets):
        self.assets = assets
        self.pending_session = None
        self.held = set()
        self.reset(get_time())

    def reset(self, now):
        self.awaiting_next_maze = False  # 도착 화면에서 새 방향키 입력을 기다린다.
        self.stage_timed_out = False
        self.size = 6
        self.completed = 0
        self.score = 0
        self.maze = Maze(self.size)
        self.player = Character(self.maze.entrance, now)
        self.now = now
        self.message = '방향키: 이동 / 벽은 두 번 공격'
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
            if self.awaiting_next_maze:
                self.advance_maze()
                return  # 확인에 쓴 방향으로 캐릭터를 이동시키지 않는다.
            self.player.position, result = self.maze.step(
                self.player.position, directions[event.key])
            self.player.react(self.now, result, directions[event.key])
            self.message = {'hit': '벽: 한 번 더 공격',
                            'broken': '벽 파괴 완료! 다시 누르면 이동',
                            'blocked': '미로의 경계입니다',
                            'moved': '방향키: 이동 / 벽은 두 번 공격',
                            'exit': '다음 미로'}[result]
            if result == 'exit':
                self.completed += 1
                if self.completed == 2:
                    battle = self.framework.modes['battle_mode']
                    battle.pending_session = (self.player.rules, self.score)
                    self.framework.change_mode('battle_mode')
                    return
                # 도착 확인 제약을 얻기 전에는 기존처럼 자동 전환한다.
                if 'maze_arrival' not in self.framework.notice.active:
                    self.advance_maze()
                    return
                self.awaiting_next_maze = True
                self.message = '아무 방향키: 다음 미로'

    def advance_maze(self):
        # 확인 입력은 이동에 쓰지 않고 직전 출구에서 다음 미로를 시작한다.
        self.now = get_time()
        self.maze = Maze(self.size, self.maze.exit)
        self.player.enter_maze(self.maze.entrance, self.now)
        self.framework.restart_stage_timer()
        self.awaiting_next_maze = False
        self.message = '방향키: 이동 / 벽은 두 번 공격'
        self.transitioned = True

    def update(self, now):
        self.now = now
        self.transitioned = False
        if not self.awaiting_next_maze:
            self.player.update(now)

    def draw(self):
        sheet, font = self.assets.maze_sheet, self.assets.font
        if self.awaiting_next_maze:
            # 미로 시트 1행 4열을 플레이 영역(100, 100)~(500, 500)에 표시한다.
            width, height = sheet.w // 4, sheet.h // 2
            sheet.clip_draw(3 * width, height, width, height, 300, 300, 400, 400)
        else:
            self.maze.draw(sheet, font, self.now)
            self.player.draw(self.assets.character_sheet, self.maze, self.now)
        draw_hud(self.assets, self.player.rules, self.now, self.completed, self.score)
        if not self.player.is_playing and not self.stage_timed_out:
            self.message = '체력이 모두 소진되었습니다'
        text(font, 100, 70, self.message)
        text(font, 100, 45, '방향키: 이동·벽 공격')
        if not self.player.is_playing:
            width, height = sheet.w // 4, sheet.h // 2
            sheet.opacify(0.5)
            try:
                sheet.clip_draw(3 * width, height, width, height,
                                400, 300, 800, 600)
            finally:
                sheet.opacify(1.0)
            text(font, 180, 320, '아래: 재시작 / 위: 시작 화면')
