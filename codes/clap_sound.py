# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""외부 음원 없이 짧은 박수 효과음을 만든다."""
from array import array
import math
import random
from pathlib import Path
from tempfile import TemporaryDirectory
import wave
from pico2d import load_wav


def load_clap():
    # rhythm_hell의 세 번 겹친 잡음과 짧은 감쇠를 PCM으로 만든다.
    rate = 44100
    samples = array('h')
    noise = random.Random(0)
    previous = 0.0
    for index in range(round(rate * .115)):
        elapsed = index / rate
