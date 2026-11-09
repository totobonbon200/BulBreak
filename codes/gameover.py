"""게임오버 판정을 표시 및 입력 처리와 분리한다."""


class GameOverRules:
    MAX_IDLE_TIME = 3.0
    ACTION_BONUS = 1.0

    def __init__(self, now=0.0):
        self.remaining = self.MAX_IDLE_TIME
        self.last_update = now

    @property
    def is_over(self):
        return self.remaining <= 0

    def update(self, now):
        elapsed = max(0.0, now - self.last_update)
        self.last_update = now
        self.remaining = max(0.0, self.remaining - elapsed)

    def record_action(self, now):
        self.update(now)
        if not self.is_over:
            self.remaining = min(self.MAX_IDLE_TIME,
                                 self.remaining + self.ACTION_BONUS)

    def enter_maze(self, now):
        self.last_update = now

    def idle_remaining(self, now):
        return max(0.0, self.remaining - max(0.0, now - self.last_update))
