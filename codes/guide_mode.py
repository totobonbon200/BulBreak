"""기본 조작과 제약 요약을 페이지별로 보여준다."""
# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
from math import cos, radians, sin
from textwrap import wrap
from pico2d import SDL_KEYDOWN, SDLK_DOWN, SDLK_RIGHT, SDLK_UP, draw_line
from codes.hud import info_text
from codes.constraints import CAT_CONSTRAINT, ConstraintNotice
from codes.maze_bomber import BomberRound
from codes.menu_modes import AnimatedSelectionMenu


def draw_key_outline(x, y):
    # 네 모서리의 호 사이를 직선으로 이어 둥근 키 윤곽을 그린다.
    corners = ((x + 60, y + 26), (x - 60, y + 26), (x - 60, y - 26), (x + 60, y - 26))
    points = [(cx + 10 * cos(radians(angle)), cy + 10 * sin(radians(angle)))
              for index, (cx, cy) in enumerate(corners)
              for angle in range(90 * index, 90 * (index + 1) + 1, 15)]
    for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1]):
        draw_line(x1, y1, x2, y2, 255, 255, 255)


class GuideMode(AnimatedSelectionMenu):
    index = property(lambda self: self.page)  # 현재 페이지가 목록의 선택 항목이다.
    # 키 좌표와 역할은 위·왼쪽·아래·오른쪽 순서로 대응한다.
    KEYS = (('↑', 550, 400), ('←', 392, 311), ('↓', 550, 311), ('→', 708, 311))
    KEY_ROLES = (('위로 이동', '좌측 이동', '아래 이동', '우측 이동'),
                 ('위로 회피', '좌측 공격', '아래 회피', '우측 공격'))

    # 기본 조작 안내는 제약이 없는 미로와 전투를 기준으로 한다.
    PAGES = (
        ('미로 조작방법', ('통로에서는 방향키를 한 번 누를 때마다 그 방향으로 한 칸 움직입니다.',
                       '앞에 벽이 있으면 같은 방향키를 두 번 눌러 부수고, 세 번째에 그 칸으로 들어갑니다.',
                       '출구에 도착하면 다음 미로로 넘어갑니다. 두 번째 출구에서는 전투가 시작됩니다.')),
        ('전투 조작방법', ('←부터 시작해 ←·→를 번갈아 공격합니다. 노란 화살표가 다음 공격 방향입니다.',
                       '적 위에 빨간 ↑·↓가 표시되면 다음 입력에서 같은 방향으로 회피합니다.',
                       '적의 가로 공격은 ←·→ 어느 쪽으로든 받아칩니다. 타격 10회 성공 시 클리어합니다.')),
        ('maze_cross', ('중앙에서 열린 출구 방향을 고릅니다.',
                        '올바른 출구를 여섯 번 고르면 미로 하나를 통과합니다.')),
        ('battle_placeholder', ('기본 전투와 동일하게 진행합니다.',)),
        ('battle_rhythm', ('두 패턴의 시범을 듣고 아무 방향키로 박자를 따라 칩니다.',
                           '판정은 ±100ms이며, 실패한 패턴마다 체력이 1 줄어듭니다.',
                           '두 패턴이 끝났을 때 체력이 남으면 다음으로 넘어갑니다.')),
        (CAT_CONSTRAINT, ('미로와 전투에서 고양이 영상과 움직이는 고양이가 시야를 가립니다.',
                          '움직이는 고양이는 화면 가장자리에서 튕깁니다.')),
        ('maze_darkness', ('기본 시야는 반지름 1.5칸이며, 주변 5×5 칸의 출구가 흐리게 보입니다.',)),
        ('battle_building', ('건물이 닿으면 좌우로 공격합니다. 층마다 열 번 타격하세요.',
                             '위 방향키로 점프하거나 가까운 건물을 띄웁니다.',
                             '바닥에서 깔리면 체력 1을 잃고 맨 아래층이 부서집니다.')),
        ('maze_bomber', (f'{BomberRound.FUSE_SECONDS:g}초 뒤 폭발하며, 체력이 남으면 다음 단계로 넘어갑니다.',
                         '폭발 범위 안에 있으면 체력이 1 줄어듭니다.')),
    )

    def __init__(self, font, title_font=None, menu_image=None):
        super().__init__(font, '가이드', (), {})
        self.title_font = title_font or font
        self.menu_image = menu_image
        self.notice = ConstraintNotice()
        self.enter(True)

    def enter(self, first_visit):
        super().enter(first_visit)
        self.page = 0
        self.progress = [0.0] * len(self.PAGES)  # 가이드 페이지마다 선택 전환을 기록한다.
        self.last_update = None

    def handle_event(self, event):
        if event.type != SDL_KEYDOWN or getattr(event, 'repeat', False):
            return
        if event.key == SDLK_RIGHT:
            self.framework.change_mode('start_mode')
        elif event.key in (SDLK_UP, SDLK_DOWN):
            step = -1 if event.key == SDLK_UP else 1
            self.page = (self.page + step) % len(self.PAGES)

    def draw_keys(self):
        for (arrow, x, y), role in zip(self.KEYS, self.KEY_ROLES[self.page]):
            draw_key_outline(x, y)
            info_text(self.title_font, x - 12, y + 14, arrow)
            self.title_font.draw(x - 46, y - 14, role, (255, 220, 0))

    def page_title(self, index):
        # 페이지 제목과 왼쪽 선택지에 같은 제약 이름을 표시한다.
        heading = self.PAGES[index][0]
        self.notice.selected = heading
        return heading if index < 2 else self.notice.title()

    def draw_page(self):
        lines = self.PAGES[self.page][1]
        if self.page < 2:
            self.draw_keys()
            info_text(self.font, 320, 250, '세부 조작')
            heading_y, detail_y = 467, 222
        else:
            heading_y, detail_y = 420, 355
        info_text(self.title_font, 320, heading_y, self.page_title(self.page))
        # 긴 안내는 오른쪽 본문 영역 안에서 줄을 나눈다.
        wrapped_lines = [part for line in lines for part in wrap(line, width=34)]
        for index, line in enumerate(wrapped_lines):
            info_text(self.font, 320, detail_y - index * 26, line)

    def draw(self):
        info_text(self.font, 24, 575, '가이드')
        self.draw_paged_options(len(self.PAGES), self.page_title)
        info_text(self.font, 655, 507, f'{self.page + 1} / {len(self.PAGES)}')
        self.draw_page()
        info_text(self.font, 24, 14, '↑ 이전  ↓ 다음')
        info_text(self.font, 605, 72, '→ 시작 화면')
