# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md의 최신 기준을 확인한다.
"""효과 없는 임시 제약과 전환 안내를 관리한다."""
from codes.hud import panel, info_text


class ConstraintNotice:
    DURATION = 1.0
    TITLES = {"maze_mode": "[미로] 임시 제약", "battle_mode": "[전투] 임시 제약"}

    def __init__(self):
        # 첫 전투를 마친 뒤부터 안내하며 새 게임에서는 초기화한다.
        self.enabled = False
        self.pending = None
        self.active = {}

    def reset(self):
        self.__init__()

    def begin(self, source, target, now):
        # 최초 미로에서 전투로 갈 때는 제약을 발동하지 않는다.
        if source == "battle_mode" and target == "maze_mode":
            self.enabled = True
        if self.enabled and source != target and {source, target} == set(self.TITLES):
            self.pending = (target, now)
            return True
        return False

    def finish(self, now):
        # 일반 게임오버와 분리하며 현재 임시 제약에는 실패 조건이 없다.
        if self.pending is None or now - self.pending[1] < self.DURATION:
            return None
        target = self.pending[0]
        self.active[target] = self.TITLES[target]
        self.pending = None
        return target

    def draw(self, font, mode):
        # 6×6 미로 기준 그림 자리는 비우고 오른쪽 두 줄만 표시한다.
        if self.pending is not None:
            panel(100, 100, 500, 500, dark=True, outline=False)
            info_text(font, 300, 400, self.TITLES[self.pending[0]])
            info_text(font, 300, 333, "효과 없음. 전환 시험용.")
        elif mode in self.active:
            info_text(font, 535, 440, self.active[mode])
            info_text(font, 535, 410, '효과 없음. 전환 시험용.')
