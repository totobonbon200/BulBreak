# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""건물부수기의 낙하, 충돌과 층별 타격 상태를 관리한다."""
from random import randint

class BuildingBattle:
    FLOOR, PLAYER_SIZE, FLOOR_HEIGHT = 130, 100, 42
    GRAVITY, HITS_PER_FLOOR = 1000, 10

    def __init__(self, now):
        self.floors = randint(3, 5)
        self.hits = 0
        self.bottom, self.fall_speed = 540, 0
        self.feet, self.jump_speed = self.FLOOR, 0
        self.updated_at = now

    def fall(self, dt):
        # 건물은 지면 위 주인공 머리 높이에서 멈춘다.
        rest = self.FLOOR + self.PLAYER_SIZE
        self.bottom = max(rest, self.bottom + self.fall_speed * dt - .5 * self.GRAVITY * dt ** 2)
        self.fall_speed = self.fall_speed - self.GRAVITY * dt if self.bottom > rest else 0
