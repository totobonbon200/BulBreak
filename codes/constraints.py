# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md의 최신 기준을 확인한다.
"""누적 제약과 전환 안내를 관리한다."""
from codes.hud import panel, info_text
import random


class ConstraintNotice:
    DURATION = 1.0
    KEYS = {'maze_mode': 'maze_arrival', 'battle_mode': 'battle_placeholder'}
    TITLES = {"maze_mode": "[미로] 도착 화면 확인", "battle_mode": "[전투] 임시 제약"}

    def __init__(self):
        # 첫 전투를 마친 뒤부터 안내하며 새 게임에서는 초기화한다.
        self.enabled = False
        self.pending = None
        self.active = set()  # 현재 선택한 제약 하나만 보관한다.
        self.selected = None

    def reset(self):
        self.__init__()

    def begin(self, source, target, now):
        # 최초 미로에서 전투로 갈 때는 제약을 발동하지 않는다.
        if source == "battle_mode" and target == "maze_mode":
            self.enabled = True
        if self.enabled and source != target and {source, target} == set(self.TITLES):
            # 안내를 시작할 때 진입 모드의 제약 하나만 미리 선택한다.
            self.selected = random.choice((self.KEYS[target],
                                           'maze_cross' if target == 'maze_mode' else 'battle_rhythm'))
            self.pending = (target, now)
            return True
        return False

    def finish(self, now):
        # 안내 완료 시 기존 제약과 신규 동작 제약을 함께 획득한다.
        if self.pending is None or now - self.pending[1] < self.DURATION:
            return None
        target = self.pending[0]
        self.active = {self.selected}  # 이전 제약을 교체하여 한 개만 적용한다.
        self.pending = None
        return target

    def description(self, mode):
        # 안내 시작 때 선택한 제약과 실제 적용 설명을 일치시킨다.
        return {'maze_arrival': '도착 후 방향키로 다음 미로', 'maze_cross': '중앙 출구 6회',
                'battle_placeholder': '추가 효과 없음',
                'battle_rhythm': '두 패턴 따라 입력·±100ms'}.get(self.selected, '')

    def draw(self, font, mode):
        # 6×6 미로 기준 그림 자리는 비우고 오른쪽 두 줄만 표시한다.
        if self.pending is not None:
            panel(100, 100, 500, 500, dark=True, outline=False)
            info_text(font, 300, 400, self.TITLES[self.pending[0]])
            info_text(font, 300, 333, self.description(self.pending[0]))
        elif self.KEYS.get(mode) in self.active:
            info_text(font, 535, 440, self.TITLES[mode])
            info_text(font, 535, 410, self.description(mode))
