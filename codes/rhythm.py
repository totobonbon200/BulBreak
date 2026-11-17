# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""시범 박자 재생과 입력·누락 판정을 관리한다."""
import json
import re
from pathlib import Path


class Rhythm:
    WINDOW = .025  # 최소 박자 간격보다 좁은 ±25ms 판정이다.
