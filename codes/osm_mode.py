"""중앙의 주인공을 향해 날아오는 노트를 맞히는 디버그 제약."""
# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
from math import cos, sin, tau
from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_DOWN, SDLK_LEFT, SDLK_RIGHT, SDLK_UP
from pico2d import draw_line, draw_rectangle
from codes.animation import draw_frame
from codes.hud import info_text
from codes.menu_modes import MenuMode
from codes.rhythm import Rhythm


class OsmMode(MenuMode):
    CENTER = (300, 300)
    TRAVEL = 1.0
    RADIUS = 180
    HIT_RADIUS = 100
    SUCCESS_SECONDS = 0.2
    # 입력과 화살표는 노트가 출발한 쪽을 가리킨다.
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
        self.success_until = self.now
        self.arrival = self.now + self.TRAVEL

    def next_note(self, now):
        # 결과를 잠깐 보여 준 뒤 다음 노트가 바깥에서 출발한다.
        self.arrival = now + self.TRAVEL + 0.2

    def update(self, now):
        self.now = now
        if self.hits < len(self.PATTERN) and now > self.arrival + Rhythm.WINDOW:
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
        on_time = Rhythm.is_on_time(now, self.arrival)
        if event.key == self.PATTERN[self.hits] and on_time:
            self.hits += 1
            self.success_until = now + self.SUCCESS_SECONDS
            self.feedback = '성공'
            self.next_note(now)
        elif now >= self.arrival - self.TRAVEL:
            self.feedback = '화살표 방향과 타이밍을 맞추세요'

    def draw(self):
        x, y = self.CENTER
        draw_rectangle(100, 100, 500, 500, 255, 255, 255)
        # 가로·세로 이동선과 중앙 판정 영역을 표시한다.
        draw_line(120, y, 480, y, 80, 80, 80)
        draw_line(x, 120, x, 480, 80, 80, 80)
        # 원 둘레에 화살표의 중심이 닿는 순간을 판정한다.
        points = [(round(x + self.HIT_RADIUS * cos(i * tau / 64)),
                   round(y + self.HIT_RADIUS * sin(i * tau / 64))) for i in range(64)]
        pulse = max(0.0, min(1.0, (self.success_until - self.now) / self.SUCCESS_SECONDS))
        shade = round(150 + 85 * pulse)
        for start, end in zip(points, points[1:] + points[:1]):
            draw_line(*start, *end, shade, shade, shade)
        sheet = self.assets.character_sheet
        draw_frame(sheet, 4, 4, (0, int(pulse > 0)), x, y, 44, 44)
        info_text(self.assets.notice_font, 100, 550, self.title)
        info_text(self.font, 530, 400, f'성공 {self.hits}/{len(self.PATTERN)}')
        info_text(self.font, 530, 360, '화살표가 원에 닿을 때 방향키')
        if self.hits == len(self.PATTERN):
            info_text(self.font, 530, 320, '클리어 · 오른쪽으로 복귀')
        else:
            info_text(self.font, 530, 320, self.feedback)
            self.draw_note()

    def draw_note(self):
        remaining = self.arrival - self.now
        if remaining > self.TRAVEL:
            return
        dx, dy = self.DIRECTIONS[self.PATTERN[self.hits]]
        distance = self.HIT_RADIUS + (self.RADIUS - self.HIT_RADIUS) * remaining / self.TRAVEL
        x, y = self.CENTER
        x, y = round(x + dx * distance), round(y + dy * distance)
        column = (SDLK_LEFT, SDLK_RIGHT, SDLK_UP, SDLK_DOWN).index(self.PATTERN[self.hits])
        draw_frame(self.assets.effect_sheet, 2, 4, (1, column), x, y, 65, 65)
