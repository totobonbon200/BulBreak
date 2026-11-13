"""A separate guide screen describing the playable maze prototype."""
from pico2d import SDL_KEYDOWN, SDLK_RIGHT
from codes.hud import text


class GuideMode:
    def __init__(self, font):
        self.font = font
        self.framework = None

    def enter(self, first_visit):
        pass

    def exit(self):
        pass

    def update(self, now):
        pass

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_RIGHT:
            self.framework.change_mode('start_mode')

    def draw(self):
        text(self.font, 70, 540, 'BulBreak - 플레이 가이드')
        sections = (
            ('이동과 탈출', (
                '방향키로 이동합니다. 출구(OUT)에 도착하면 다음 미로로 넘어갑니다.',
                '벽은 두 번 눌러 부순 뒤, 한 번 더 눌러 이동합니다.',
                '키는 눌렀다 떼어야 합니다. 길게 누르는 것은 연속 입력이 아닙니다.')),
            ('게임오버 기준: 체력과 무행동 시간', (
                '체력 3개로 시작합니다. 무행동 시간이 소진될 때마다 체력이 1 줄어듭니다.',
                '방향키를 누르면 1초 회복하며 현재 최대 시간을 넘지 않습니다.',
                '최대 시간은 3초부터 다음 미로마다 0.05초씩 줄어 최소 1초가 됩니다.',
                '미로 전환 중 시간은 소모되지 않습니다. 체력은 회복되지 않습니다.')),
            ('공통 15초 제한과 재시작', (
                '선택된 기준과 관계없이 미로·전투 진입 후 15초가 지나면 게임오버됩니다.',
                '다음 미로 진입 시 15초 제한은 초기화되며, 입력으로 늘어나지 않습니다.',
                '게임오버 후 아래는 재시작, 위는 시작 화면으로 돌아가기입니다.',)),
            ('현재 구현 범위', (
                '미로는 반복됩니다. 전투와 제약시스템 플레이는 아직 구현되지 않았습니다.',)),
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
