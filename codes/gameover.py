# 이곳에는 게임오버기준 3가지를 만들어서 여기서 조건을 충족하는지 검사할 것
"""게임오버 판정을 표시 및 입력 처리와 분리한다."""
import random


class GameOverRules:
    MAX_IDLE_TIME = 3.0
    ACTION_BONUS = 1.0
    MAZE_LIMIT = 3.0

    def __init__(self, now=0.0, rule=None, mode="battle"):
        self.mode = mode
        self.rule = 1 if rule is None else rule
        self.max_idle_time = self.MAX_IDLE_TIME
        if self.rule not in (1, 2, 3):
            raise ValueError(self.rule)
        self.remaining = self.MAX_IDLE_TIME
        self.last_update = now
        self.health = 3
        self.maze_elapsed = 0.0

    @property
    def is_over(self):
        return self.health <= 0

    @property
    def animation_frame_seconds(self):
        """미로와 같은 기본 0.15초 간격을 최대 타이머에 비례 조정한다."""
        return min(0.15, max(0.075, 0.075 + (self.max_idle_time - 1.0) * 0.0375))

    def update(self, now):
        elapsed = max(0.0, now - self.last_update)
        self.last_update = now
        self.remaining -= elapsed
        while self.remaining <= 0 and self.health > 0:
            self.health -= 1
            self.remaining += self.max_idle_time
        if self.is_over:
            self.remaining = 0.0

    def record_action(self, now):
        self.update(now)
        if self.mode == "battle" and not self.is_over:
            self.remaining = min(self.max_idle_time,
                                 self.remaining + self.ACTION_BONUS)

    def enter_maze(self, now):
        self.mode = "maze"
        self.last_update = now
        self.max_idle_time = self.MAZE_LIMIT
        self.remaining = self.MAZE_LIMIT

    def enter_battle(self, now):
        self.mode = "battle"
        self.last_update = now

    def record_wrong_defense(self, health_damage=0):
        self.remaining = max(0.0, self.remaining - 0.5)
        self.health = max(0, self.health - health_damage)
        if self.remaining <= 0:
            self.health = 0
        if self.is_over:
            self.remaining = 0.0

    def idle_remaining(self, now):
        return max(0.0, self.remaining - max(0.0, now - self.last_update))
