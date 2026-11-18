"""A separate guide screen describing the playable maze prototype."""
# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
from pico2d import SDL_KEYDOWN, SDLK_DOWN, SDLK_RIGHT, SDLK_UP
from codes.hud import info_text, text
from codes.constraints import CAT_CONSTRAINT, ConstraintNotice


class GuideMode:
    # 기본 조작 안내는 제약이 없는 미로와 전투를 기준으로 한다.
    PAGES = (
        ('미로 조작방법', ('방향키로 한 칸 이동합니다.',
                       '벽 방향을 두 번 눌러 부순 뒤, 한 번 더 눌러 그 칸으로 들어갑니다.',
                       '미로 출구에 두 번 도착하면 전투로 넘어갑니다.')),
        ('전투 조작방법', ('←부터 시작해 ←·→를 번갈아 눌러 공격합니다. 노란 화살표가 다음 공격 방향입니다.',
                       '적이 위·아래로 공격하면 빨간 화살표와 같은 방향으로 회피합니다.',
                       '적의 가로 공격은 ←·→ 어느 쪽으로든 받아칠 수 있습니다. 공격 10회 성공 시 클리어합니다.')),
        ('maze_arrival', ('다음 미로로 이어지는 출구에 도착하면 도착 화면이 표시됩니다.',
                          '아무 방향키나 새로 한 번 누르면 다음 미로로 넘어갑니다.')),
        ('maze_cross', ('중앙에서 열린 출구 방향을 고릅니다.',
                        '올바른 출구를 여섯 번 고르면 미로 하나를 통과합니다.')),
        ('battle_placeholder', ('기본 전투와 동일하게 진행합니다.',)),
        ('battle_rhythm', ('두 패턴의 시범을 듣고 아무 방향키로 박자를 따라 칩니다.',
                           '판정 범위는 ±100ms이며, 틀리거나 놓치면 체력이 줄어듭니다.')),
        (CAT_CONSTRAINT, ('미로와 전투에서 고양이 사진과 움직이는 고양이가 시야를 가립니다.',
                          '움직이는 고양이는 화면 가장자리에서 튕깁니다.')),
    )

    def __init__(self, font, title_font=None):
        self.font = font
        self.title_font = title_font or font
        self.notice = ConstraintNotice()
        self.page = 0
        self.framework = None

    def enter(self, first_visit):
        self.page = 0

    def exit(self):
        pass

    def update(self, now):
        pass

    def handle_event(self, event):
        if event.type != SDL_KEYDOWN or getattr(event, 'repeat', False):
            return
        if event.key == SDLK_RIGHT:
            self.framework.change_mode('start_mode')
        elif event.key in (SDLK_UP, SDLK_DOWN):
            step = -1 if event.key == SDLK_UP else 1
            self.page = max(0, min(self.page + step, len(self.PAGES) - 1))

    def draw_page(self):
        heading, lines = self.PAGES[self.page]
        if self.page >= 2:
            self.notice.selected = heading
            heading = self.notice.title()
        info_text(self.title_font, 80, 420, heading)
        for index, line in enumerate(lines):
            info_text(self.font, 80, 355 - index * 34, line)

    def draw(self):
        info_text(self.font, 80, 507, '가이드')
        info_text(self.font, 655, 507, f'{self.page + 1} / {len(self.PAGES)}')
        self.draw_page()
        info_text(self.font, 80, 72, '↑ 이전  ↓ 다음')
        info_text(self.font, 605, 72, '→ 시작 화면')

    def _draw_legacy(self):
        text(self.font, 70, 540, 'BulBreak - 플레이 가이드')
        sections = (
            ('이동과 탈출', (
                '방향키로 이동합니다. 출구에 도착하면 다음 미로로 넘어갑니다.',
                '벽은 두 번 눌러 부순 뒤, 한 번 더 눌러 이동합니다.',
                '키는 눌렀다 떼어야 합니다. 길게 누르는 것은 연속 입력이 아닙니다.')),
            ('게임오버 기준: 체력과 무행동 시간', (
                '체력 3개로 시작합니다. 무행동 시간이 소진될 때마다 체력이 1 줄어듭니다.',
                '미로는 고정 3초 이내 주파가 기준이며 입력으로 시간을 회복하지 않습니다.',
                '다음 미로에서 3초로 초기화합니다. 전투는 기존 무행동 타이머를 사용합니다.',
                '미로 전환 중 시간은 소모되지 않습니다. 체력은 회복되지 않습니다.')),
            ('공통 15초 제한과 재시작', (
                '선택된 기준과 관계없이 미로·전투 진입 후 15초가 지나면 게임오버됩니다.',
                '다음 미로 진입 시 15초 제한은 초기화되며, 입력으로 늘어나지 않습니다.',
                '게임오버 메뉴는 위·아래로 고르고 왼쪽으로 실행합니다.',)),
            ('현재 구현 범위', (
                '미로 2회 후 전투: 좌우 공격 10회 성공 시 다시 미로로 돌아갑니다.',)),
        )
        y = 490
        for title, lines in sections:
            text(self.font, 70, y, title)
            y -= 28
            for line in lines:
                text(self.font, 70, y, line)
                y -= 26
            y -= 18
        text(self.font, 70, 45, '오른쪽 방향키: 시작 화면으로 돌아가기')
