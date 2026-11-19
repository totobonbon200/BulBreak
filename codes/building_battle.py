# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""건물부수기의 낙하, 충돌과 층별 타격 상태를 관리한다."""
from random import randint

class BuildingBattle:
    FLOOR, PLAYER_SIZE, FLOOR_HEIGHT = 130, 100, 42
    GRAVITY, HITS_PER_FLOOR = 1000, 10

    def __init__(self, now):
        self.floors = randint(3, 5)
