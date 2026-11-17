# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""시범 박자 재생과 입력·누락 판정을 관리한다."""
import json
import re
from pathlib import Path


class Rhythm:
    WINDOW = .025  # 최소 박자 간격보다 좁은 ±25ms 판정이다.

    def __init__(self, now):
        # 사용자 원본을 수정하지 않고 시범 페이지의 박자 목록을 읽는다.
        source = Path(__file__).resolve().parents[1] / 'resources/rhythm_hell'
        data = re.search(r'const segments = (\[.*?\]);', source.read_text(encoding='utf-8'))
        self.patterns = [part['hits'] for part in json.loads(data.group(1))]
        self.started = now
        self.segment = 0
        self.index = 0
