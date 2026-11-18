# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""리듬 시작 전에 같은 간격으로 숫자와 GO를 표시한다."""
from math import pi, sin


class RhythmCountdown:
    LABELS = ('3', '2', '1', 'GO')
    STEP = 0.625

    def __init__(self, now):
        self.started = now
        self.end = now + len(self.LABELS) * self.STEP

    def frame(self, now):
        if not self.started <= now < self.end:
            return None
        index, progress = divmod((now - self.started) / self.STEP, 1)
        scale = 1 + .16 * sin(pi * progress ** .55)  # 초반에 커지고 끝까지 부드럽게 줄어든다.
        return self.LABELS[int(index)], scale
