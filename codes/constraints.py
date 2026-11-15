# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md의 최신 기준을 확인한다.
"""효과 없는 임시 제약과 전환 안내를 관리한다."""
from codes.hud import panel, info_text


class ConstraintNotice:
    DURATION = 1.5
    TITLES = {"maze_mode": "[미로] 임시 제약", "battle_mode": "[전투] 임시 제약"}