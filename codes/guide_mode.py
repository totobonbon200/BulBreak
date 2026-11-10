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
            ('KEEP MOVING', (
                'Idle time starts at 3 seconds. Each press restores 1 second (max 3).',
                'You start with 3 HP. Every 3 seconds in a maze costs 1 HP.',
                'Reaching OUT restarts the HP countdown, but does not refill HP.',
                'Zero idle time or zero HP means GAME OVER.')),
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
