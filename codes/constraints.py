# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md의 최신 기준을 확인한다.
"""누적 제약과 전환 안내를 관리한다."""
from codes.hud import panel, info_text


class ConstraintNotice:
    DURATION = 1.0
    KEYS = {'maze_mode': 'maze_arrival', 'battle_mode': 'battle_placeholder'}
    TITLES = {"maze_mode": "[미로] 도착 화면 확인", "battle_mode": "[전투] 임시 제약"}

    def __init__(self):
        # 첫 전투를 마친 뒤부터 안내하며 새 게임에서는 초기화한다.
        self.enabled = False
        self.pending = None
        self.active = set()  # 기존 제약을 유지하며 같은 제약의 중복을 막는다.

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
        # 안내 완료 시 기존 제약과 신규 동작 제약을 함께 획득한다.
        if self.pending is None or now - self.pending[1] < self.DURATION:
            return None
        target = self.pending[0]
        self.active.add(self.KEYS[target])
        # 기존 제약과 새 동작 제약을 함께 누적한다.
        self.active.add('maze_cross' if target == 'maze_mode' else 'battle_rhythm')
        self.pending = None
        return target

    def description(self, mode):
        # 도착 확인·무효과 제약에 추가된 중앙 이동·리듬 입력을 안내한다.
        return '중앙 출구 6회·도착 확인' if mode == 'maze_mode' else '시범 따라 입력·±25ms'

    def draw(self, font, mode):
        # 6×6 미로 기준 그림 자리는 비우고 오른쪽 두 줄만 표시한다.
        if self.pending is not None:
            panel(100, 100, 500, 500, dark=True, outline=False)
            info_text(font, 300, 400, self.TITLES[self.pending[0]])
            info_text(font, 300, 333, self.description(self.pending[0]))
        elif self.KEYS.get(mode) in self.active:
            info_text(font, 535, 440, self.TITLES[mode])
            info_text(font, 535, 410, self.description(mode))
