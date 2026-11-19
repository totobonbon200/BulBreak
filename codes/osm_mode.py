"""중앙의 주인공을 향해 날아오는 노트를 맞히는 디버그 제약."""
# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_DOWN, SDLK_LEFT, SDLK_RIGHT, SDLK_UP
from pico2d import draw_line, draw_rectangle
from codes.hud import info_text
from codes.menu_modes import MenuMode


class OsmMode(MenuMode):
    CENTER = (300, 300)
    TRAVEL = 1.0
    WINDOW = 0.15
    RADIUS = 180
    # 입력 방향은 노트가 주인공을 향해 이동하는 방향이다.
    DIRECTIONS = {SDLK_UP: (0, 1), SDLK_DOWN: (0, -1),
                  SDLK_LEFT: (-1, 0), SDLK_RIGHT: (1, 0)}
    PATTERN = (SDLK_RIGHT, SDLK_DOWN, SDLK_LEFT, SDLK_UP,
               SDLK_LEFT, SDLK_DOWN, SDLK_RIGHT, SDLK_UP)

    def __init__(self, assets):
        super().__init__(assets.font, '[미로] OSM', (), {})
        self.assets = assets

    def enter(self, first_visit):
        super().enter(first_visit)
        # 목록에서 다시 시작하면 첫 노트부터 진행한다.
        self.hits = 0
        self.feedback = ''
        self.now = self.framework.clock()
        self.arrival = self.now + self.TRAVEL

    def next_note(self, now):
        # 결과를 잠깐 보여 준 뒤 다음 노트가 바깥에서 출발한다.
        self.arrival = now + self.TRAVEL + 0.2

    def update(self, now):
        self.now = now
        if self.hits < len(self.PATTERN) and now > self.arrival + self.WINDOW:
            self.feedback = '놓침 · 다시 시도'
            self.next_note(now)

    def handle_event(self, event):
        if event.type == SDL_KEYUP:
            self.held.discard(event.key)
        if event.type != SDL_KEYDOWN or event.key not in self.DIRECTIONS:
            return
        if event.key in self.held or getattr(event, 'repeat', False):
            return
        self.held.add(event.key)
        if self.hits == len(self.PATTERN):
            if event.key == SDLK_RIGHT:
                self.framework.change_mode('instrument_mode')
            return
        now = self.framework.clock()
        on_time = self.arrival - self.WINDOW <= now <= self.arrival + self.WINDOW
        if event.key == self.PATTERN[self.hits] and on_time:
            self.hits += 1
            self.feedback = '성공'
            self.next_note(now)
