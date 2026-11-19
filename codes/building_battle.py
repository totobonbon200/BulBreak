# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""건물부수기의 낙하, 충돌과 층별 타격 상태를 관리한다."""
from random import randint
from pico2d import draw_line
from codes.hud import info_text

class BuildingBattle:
    CENTER_X, WIDTH = 350, 190
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

    def update(self, now):
        if now <= self.updated_at:
            return
        dt = now - self.updated_at
        self.updated_at = now
        self.fall(dt * .5)  # 건물의 상승과 낙하에 걸리는 시간을 두 배로 늘린다.
        # 공중에서도 건물이 내려오면 주인공의 머리가 밑면을 통과하지 않는다.
        limit = self.bottom - self.PLAYER_SIZE
        next_feet = self.feet + self.jump_speed * dt - .5 * self.GRAVITY * dt ** 2
        self.feet = min(limit, max(self.FLOOR, next_feet))
        self.jump_speed = self.jump_speed - self.GRAVITY * dt if self.FLOOR < self.feet < limit else 0

    @property
    def gap(self):
        # 주인공 머리에서 건물 밑면까지의 수직 간격이다.
        return self.bottom - (self.feet + self.PLAYER_SIZE)

    def jump(self):
        # 건물이 가까우면 건물을 띄우고, 떨어져 있으면 바닥에서만 점프한다.
        if self.gap <= 10:
            self.fall_speed = 475
            return True
        if self.feet == self.FLOOR:
            self.jump_speed = 340
            return True
        return False

    def attack(self):
        # 맞닿은 맨 아래층의 내구도를 소모하며 윗층은 다시 떨어진다.
        if self.floors == 0 or self.gap > 1:
            return False
        self.hits = (self.hits + 1) % self.HITS_PER_FLOOR
        if self.hits == 0:
            self.floors -= 1
            self.bottom += self.FLOOR_HEIGHT
        return True

    def draw(self, assets):
        # 메뉴 패널을 한 층씩 쌓고 주인공이 서는 바닥을 표시한다.
        draw_line(120, self.FLOOR, 490, self.FLOOR, 255, 255, 255)
        for floor in range(self.floors):
            y = self.bottom + (floor + .5) * self.FLOOR_HEIGHT
            assets.menu_image.draw(self.CENTER_X, y, self.WIDTH, self.FLOOR_HEIGHT)
        info_text(assets.font, 145, 85, '←·→ 타격   ↑ 점프 / 건물 띄우기')
        if self.floors:
            remaining = self.HITS_PER_FLOOR - self.hits
            info_text(assets.font, 275, self.bottom + 21, f'맨 아래층 내구도 {remaining}')
