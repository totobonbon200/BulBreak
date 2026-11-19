# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md의 최신 기준을 확인한다.
"""무작위 단일 제약과 전환 안내를 관리한다."""
from codes.hud import panel, info_text
from ctypes import byref, c_int
from sdl2.sdlttf import TTF_SizeUTF8
import random

CAT_CONSTRAINT = 'cat'

def draw_notice_title(font, title):
    # 실제 글자 폭으로 400×400 플레이 영역의 가운데를 맞춘다.
    width = c_int()
    TTF_SizeUTF8(font.font, title.encode('utf-8'), byref(width), None)
    info_text(font, 300 - width.value / 2, 300, title)


class ConstraintNotice:
    DURATION = 1.0
    OPTIONS = {'maze_mode': ('maze_cross', CAT_CONSTRAINT, 'maze_darkness', 'maze_bomber'),
               'battle_mode': ('battle_placeholder', 'battle_rhythm', CAT_CONSTRAINT, 'battle_building')}

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
        if self.enabled and source != target and {source, target} == set(self.OPTIONS):
            # 안내를 시작할 때 진입 모드의 제약 하나만 미리 선택한다.
            self.selected = random.choice(self.OPTIONS[target])
            self.pending = (target, now)
            return True
        return False

    def finish(self, now):
        # 안내 완료 시 미리 선택한 단일 제약으로 교체한다.
        if self.pending is None or now - self.pending[1] < self.DURATION:
            return None
        target = self.pending[0]
        self.active = {self.selected}  # 이전 제약을 교체하여 한 개만 적용한다.
        self.pending = None
        return target

    def description(self, mode):
        # 안내 시작 때 선택한 제약과 실제 적용 설명을 일치시킨다.
        return {'maze_cross': '중앙 출구 6회',
                'maze_darkness': '주인공 주변만 보이는 미로',
                'maze_bomber': '2초 뒤 십자 폭탄 3개의 범위를 피하세요',
                'battle_placeholder': '추가 효과 없음',
                'battle_building': '접촉 중 좌우 타격 · 위로 점프 또는 띄우기',
                CAT_CONSTRAINT: f'{"미로" if mode == "maze_mode" else "전투"} 시야를 가리는 고양이',
                'battle_rhythm': '두 패턴 따라 입력·±100ms'}.get(self.selected, '')

    def draw(self, font):
        if self.pending is not None:
            panel(100, 100, 500, 500, dark=True, outline=False)
            draw_notice_title(font, self.title())

    def title(self):
        # 전환 안내와 디버그 메뉴가 같은 제약 이름을 표시한다.
        return {'maze_cross': '[미로] 중앙 출구',
                'maze_darkness': '[미로] 어두ComCom',
                'maze_bomber': '[미로] 봄버맨',
                'battle_building': '[전투] 건물부수기',
                CAT_CONSTRAINT: '고양이다아아아아',
                'battle_placeholder': '[전투] 기본', 'battle_rhythm': '[전투] 리듬'}.get(self.selected, '')
