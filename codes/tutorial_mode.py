# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""첫 게임에서 미로·전투·제약을 직접 익히는 튜토리얼."""
from collections import deque
from pico2d import (SDL_KEYDOWN, SDL_KEYUP, SDLK_DOWN, SDLK_LEFT, SDLK_RIGHT, SDLK_UP,
                    draw_rectangle, get_canvas_height, get_canvas_width)
from codes.hud import info_text


def dim_outside(focus):
    # 강조 영역 주변의 네 구역에만 검은색 70%를 합성한다.
    left, bottom, right, top = focus
    width, height = get_canvas_width(), get_canvas_height()
    regions = ((0, 0, left, height), (right, 0, width, height),
               (left, 0, right, bottom), (left, top, right, height))
    for region in regions:
        draw_rectangle(*region, 0, 0, 0, 179, filled=True)


class TutorialMode:
    MAZE_STEPS = (
        (SDLK_RIGHT, '→ 로 통로를 한 칸 이동하세요.', (100, 432, 234, 500)),
        (SDLK_RIGHT, '→ 로 앞의 벽을 한 번 공격하세요.', (166, 432, 301, 500)),
        (SDLK_RIGHT, '→ 를 다시 눌러 벽을 부수세요.', (166, 432, 301, 500)),
        (SDLK_RIGHT, '→ 로 벽이 있던 칸에 들어가세요.', (166, 432, 301, 500)),
        (SDLK_RIGHT, '→ 로 출구에 도착하세요.', (232, 432, 368, 500)),
    )
    BATTLE_STEPS = (
        (SDLK_LEFT, '← 로 첫 공격을 하세요. 노란 화살표는 다음 공격 방향입니다.', (170, 125, 435, 340)),
        (SDLK_UP, '적 위의 빨간 ↑를 보고 ↑ 로 회피하세요.', (170, 125, 435, 500)),
        (SDLK_RIGHT, '→ 로 다음 공격을 하세요. 좌우를 번갈아 공격합니다.', (170, 125, 435, 340)),
        (SDLK_DOWN, '이번에는 빨간 ↓를 보고 ↓ 로 회피하세요.', (170, 125, 435, 500)),
    )
    CAT_STEP = (SDLK_DOWN, '고양이가 시야를 가립니다. ↓ 를 눌러 본 게임을 시작하세요.', (100, 100, 500, 500))
    STEPS = MAZE_STEPS + BATTLE_STEPS + (CAT_STEP,)

    def __init__(self, assets, marker):
        self.assets = assets
        self.marker = marker
        self.completed = marker.is_file()
        self.framework = None
        self.held = set()

    def enter(self, first_visit):
        self.step = 0
        self.held.clear()
        self.now = self.framework.clock()
        self.framework.notice.reset()
        self.mode = self.framework.modes['maze_mode']
        self.mode.enter(False)
        self.prepare_maze()

    def prepare_maze(self):
        # 첫 줄에서 통로 한 칸, 벽 한 칸, 출구를 순서대로 밟는다.
        maze = self.mode.maze
        maze.walls.pop((0, 1), None)
        maze.walls.pop((0, 3), None)
        maze.walls[0, 2] = 2
        maze.exit = (0, 3)

    def enter_battle(self):
        self.mode.exit()
        self.mode = self.framework.modes['battle_mode']
        self.mode.enter(False)
        self.mode.enemy.directions = deque(('up', 'down', 'left', 'right', 'up'))

    def update(self, now):
        self.now = now
        # 캐릭터 애니메이션은 진행하고 연습 타이머는 멈춘다.
        rules = self.mode.player.rules if self.step < len(self.MAZE_STEPS) else self.mode.rules
        rules.last_update = now
        self.mode.update(now)

    def handle_event(self, event):
        if event.type == SDL_KEYUP:
            self.held.discard(event.key)
            self.mode.handle_event(event)
            return
        if event.type == SDL_KEYDOWN and event.key == self.STEPS[self.step][0]:
            if event.key not in self.held and not getattr(event, 'repeat', False):
                self.held.add(event.key)
                self.advance(event)

    def advance(self, event):
        if self.step == len(self.STEPS) - 1:
            self.finish()
            return
        self.mode.handle_event(event)
        self.step += 1
        if self.step == len(self.MAZE_STEPS):
            self.enter_battle()

    def finish(self):
        self.completed = True
        try:
            self.marker.touch(exist_ok=True)
        except OSError:
            pass  # 쓰기가 제한된 경우에도 현재 실행에서는 본 게임으로 넘어간다.
        self.framework.change_mode('maze_mode')

    def exit(self):
        self.mode.exit()
        if self.assets.cat_effect is not None:
            self.assets.cat_effect.sync(False, self.now)

    @property
    def showing_cats(self):
        return self.step == len(self.STEPS) - 1
