"""A separate guide screen describing the playable maze prototype."""
from pico2d import SDL_KEYDOWN, SDLK_RIGHT


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
        self.font.draw(70, 540, 'BulBreak - 플레이 가이드', (255, 255, 255))
        sections = (
            ('이동과 탈출', (
                '방향키로 이동합니다. 출구(OUT)에 도착하면 다음 미로로 넘어갑니다.',
                '벽은 두 번 눌러 부순 뒤, 한 번 더 눌러 이동합니다.',
                '키는 눌렀다 떼어야 합니다. 길게 누르는 것은 연속 입력이 아닙니다.')),
            ('게임오버 기준: 새 게임마다 1번 또는 2번 중 하나만 추첨', (
                '1번: 무행동 시간이 0초면 종료됩니다. 입력마다 1초 회복하며 최대 3초입니다.',
                '2번: 체력 3개로 시작하며, 같은 미로에 머무르면 3초마다 체력이 1 줄어듭니다.',
                '2번에서 출구에 도착하면 체력 감소 주기만 초기화됩니다. 체력은 회복되지 않습니다.',
                '선택된 기준은 다음 미로에서도 유지됩니다. 재시작하면 다시 추첨합니다.')),
            ('STAGE DEADLINE', (
                'Each maze or battle has a separate 15-second limit.',
                'Inputs cannot extend it. At 15 seconds, the run ends.',)),
            ('CURRENT VERSION', (
                'Mazes repeat. Combat and constraint gameplay are not available yet.',)),
        )
        y = 490
        for title, lines in sections:
            self.font.draw(70, y, title, (255, 220, 100))
            y -= 28
            for line in lines:
                self.font.draw(70, y, line, (255, 255, 255))
                y -= 26
            y -= 18
        self.font.draw(70, 45, '오른쪽 방향키: 시작 화면으로 돌아가기', (255, 220, 100))
