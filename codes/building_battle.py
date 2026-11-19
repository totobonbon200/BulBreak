# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""건물부수기의 낙하, 충돌과 층별 타격 상태를 관리한다."""
from random import randint
from pico2d import draw_line
from codes.hud import info_text

class BuildingBattle:
    CENTER_X, WIDTH = 350, 190
    FLOOR, PLAYER_SIZE, FLOOR_HEIGHT = 130, 100, 42
    GRAVITY, HITS_PER_FLOOR = 1000, 10
    BUILDING_RATE = .5
    CONTACT_SECONDS = .45  # 공중에서 밑면을 따라가는 시간이다.

    def __init__(self, now):
        self.floors = randint(3, 5)
        self.hits = 0
        self.bottom, self.fall_speed = 540, 0
        self.feet, self.jump_speed = self.FLOOR, 0
        self.player_gravity = self.GRAVITY
        self.follow_until = None
        self.impact_at = None
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
        self.fall(dt * self.BUILDING_RATE)
        # 공중에서도 건물이 내려오면 주인공의 머리가 밑면을 통과하지 않는다.
        limit = self.bottom - self.PLAYER_SIZE
        if self.follow_until is not None:
            self.follow_bottom(limit, now)
            return
        next_feet = self.feet + self.jump_speed * dt - .5 * self.player_gravity * dt ** 2
        if limit > self.FLOOR and next_feet >= limit:
            self.follow_until = now + self.CONTACT_SECONDS
            self.impact_at = now
            self.follow_bottom(limit, now)
            return
        self.feet = min(limit, max(self.FLOOR, next_feet))
        self.jump_speed = self.jump_speed - self.player_gravity * dt if self.FLOOR < self.feet < limit else 0

    @property
    def gap(self):
        # 주인공 머리에서 건물 밑면까지의 수직 간격이다.
        return self.bottom - (self.feet + self.PLAYER_SIZE)

    def follow_bottom(self, limit, now):
        # 접촉 중에는 건물의 실제 속도를 따르고, 놓이면 조금 더 빠르게 떨어진다.
        self.feet = limit
        self.jump_speed = self.fall_speed * self.BUILDING_RATE
        if now >= self.follow_until:
            self.follow_until = None
            self.jump_speed = min(0, self.jump_speed) - 30
            self.player_gravity = 300

    def jump(self):
        # 건물이 가까우면 건물을 띄우고, 떨어져 있으면 바닥에서만 점프한다.
        if self.gap <= 10:
            self.fall_speed = 475
            return True
        if self.feet == self.FLOOR:
            self.jump_speed = 520  # 자유 점프의 꼭짓점은 건물의 상승 높이보다 높다.
            self.player_gravity = self.GRAVITY
            return True
        return False

    def attack(self):
        # 맞닿은 맨 아래층의 내구도를 소모하며 윗층은 다시 떨어진다.
        if self.floors == 0 or self.gap > 1:
            return False
        self.hits = (self.hits + 1) % self.HITS_PER_FLOOR
        if self.hits == 0:
            self.follow_until = None
            self.floors -= 1
            self.bottom += self.FLOOR_HEIGHT
        return True

    def draw(self, assets):
        # 메뉴 패널을 한 층씩 쌓고 주인공이 서는 바닥을 표시한다.
        draw_line(120, self.FLOOR, 490, self.FLOOR, 255, 255, 255)
        for floor in range(self.floors):
            y = self.bottom + (floor + .5) * self.FLOOR_HEIGHT
            assets.menu_image.draw(self.CENTER_X, y, self.WIDTH, self.FLOOR_HEIGHT)
        info_text(assets.font, 95, 85, '←·→ 타격   ↑ 점프 / 건물 띄우기')
        if self.floors:
            remaining = self.HITS_PER_FLOOR - self.hits
            info_text(assets.font, 95, self.bottom + 21, f'맨 아래층 내구도 {remaining}')
