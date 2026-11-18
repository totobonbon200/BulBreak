# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""고양이 제약의 캔버스 반사와 시야 방해를 그린다."""
from math import ceil, cos, sin, sqrt, tau
from random import randint, uniform

CAT_SIZE = 100
CAT_MARGIN = ceil(CAT_SIZE / sqrt(2))  # 회전한 사각형도 캔버스 안에 둔다.

def bounce_position(origin, distance, size):
    span = size - 2 * CAT_MARGIN
    return CAT_MARGIN + span - abs((origin - CAT_MARGIN + distance) % (2 * span) - span)


class CatMotion:
    def __init__(self, width, height):
        # 개체마다 시작 위치, 이동 방향과 속도를 따로 뽑는다.
        self.origin = (uniform(CAT_MARGIN, width - CAT_MARGIN),
                       uniform(CAT_MARGIN, height - CAT_MARGIN))
        self.heading = uniform(0, tau)
        self.speed = uniform(360, 480)

    def pose(self, elapsed, width, height):
        distance = elapsed * self.speed
        x = bounce_position(self.origin[0], distance * cos(self.heading), width)
        y = bounce_position(self.origin[1], distance * sin(self.heading), height)
        angle = (self.heading + distance / (CAT_SIZE / 2) * 0.85) % tau
        return x, y, angle


class CatEffect:
    # 공유 이미지와 활성 구간마다 새로 배치할 개체를 관리한다.
    def __init__(self, backdrop, sprite, width, height):
        self.backdrop, self.sprite = backdrop, sprite
        self.width, self.height = width, height
        self.started, self.cats = None, []

    def sync(self, active, now):
        if not active:
            self.started, self.cats = None, []
        elif self.started is None:
            self.started = now
            self.cats = [CatMotion(self.width, self.height) for _ in range(randint(3, 4))]
        return active

    def draw_background(self):
        # 원본의 비율을 맞추고 캔버스를 채우도록 가운데를 확대한다.
        scale = max(self.width / self.backdrop.w, self.height / self.backdrop.h)
        self.backdrop.opacify(0.55)
        self.backdrop.draw(self.width / 2, self.height / 2,
                           self.backdrop.w * scale, self.backdrop.h * scale)

    def draw_cats(self, now):
        # PNG 위쪽의 빈 여백을 잘라 회전 중심을 고양이에 맞춘다.
        elapsed = max(0.0, now - self.started)
        for cat in self.cats:
            x, y, angle = cat.pose(elapsed, self.width, self.height)
            self.sprite.clip_composite_draw(0, 0, self.sprite.w, 1080, angle, '',
                                            x, y, CAT_SIZE, CAT_SIZE)
