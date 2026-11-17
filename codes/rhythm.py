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
        self.last_clap = now - .001  # 첫 박자도 한 번 재생한다.

    @property
    def hits(self):
        return self.patterns[self.segment % len(self.patterns)]

    def advance(self, now):
        # 시범 2초 뒤 같은 박자를 입력하고 다음 시범으로 진행한다.
        misses = 0
        while now > self.started + 4:
            misses += len(self.hits) - self.index
            self.segment += 1
            self.started += 4
            self.index = 0
        while (self.index < len(self.hits)
               and now > self.started + 2 + self.hits[self.index] / 1000 + self.WINDOW):
            misses += 1
            self.index += 1
        return misses

    def press(self, now):
        # 박자 하나를 한 번만 소비하며 구간 밖 입력도 실패로 판정한다.
        if self.index >= len(self.hits):
            return False
        expected = self.started + 2 + self.hits[self.index] / 1000
        if abs(now - expected) > self.WINDOW + 1e-9:
            return False
        self.index += 1
        return True

    def frame(self, now):
        # 시범의 각 박자에서 1행 2열을 짧게 보여 준비 동작을 만든다.
        elapsed = now - self.started
        pulse = elapsed < 2 and any(0 <= elapsed - hit / 1000 < .04 for hit in self.hits)
        return 0, int(pulse)

    def description(self, now):
        return '시범 박자 확인' if now < self.started + 2 else '같은 박자 입력 (±25ms)'

    def play_claps(self, now, sound):
        # 현재 시범 박자만 재생하며 프레임 지연으로 지난 소리는 버린다.
        for hit in self.hits:
            onset = self.started + hit / 1000
            if self.last_clap < onset <= now and now - onset < .05:
                if sound is not None:
                    sound.play()
        self.last_clap = now

    def beat_times(self, response=True):
        # 시범·입력의 소리와 판정이 공유하는 절대 박자 시각이다.
        phase = 2 if response else 0
        return [self.started + phase + hit / 1000 for hit in self.hits]
