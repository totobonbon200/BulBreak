# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""고양이 제약의 캔버스 반사와 시야 방해를 그린다."""
from math import ceil, sqrt
from random import uniform

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
        self.heading = uniform(0, 2 * 3.141592653589793)
        self.speed = uniform(360, 480)
