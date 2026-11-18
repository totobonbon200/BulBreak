# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""외부 음원 없이 리듬 전투의 짧은 효과음을 만든다."""
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
        envelope = .17 * math.exp(-elapsed * 45)
        for offset, strength in ((0, .53), (.009, .36), (.018, .4)):
            if elapsed >= offset:
                envelope += strength * math.exp(-(elapsed - offset) * 230)
        white = noise.uniform(-1, 1)
        value = (white - previous * .7) * envelope * .65
        samples.append(round(max(-1, min(1, value)) * 32767))
        previous = white
    return load_pcm(samples, rate)


def load_glass_break():
    rate = 44100
    noise = random.Random(47)
    samples = array('h', (round(32767 * glass_sample(index / rate, noise.uniform(-1, 1)))
                          for index in range(round(rate * .15))))
    return load_pcm(samples, rate)


def glass_sample(elapsed, noise):
    # 짧은 파열 뒤에 서로 다른 높은 음이 빠르게 감쇠한다.
    strike = noise * .26 * math.exp(-elapsed * 92)
    partials = ((1730, .14, 28), (2860, .09, 38), (4370, .06, 53))
    ringing = sum(gain * math.sin(math.tau * freq * elapsed) * math.exp(-decay * elapsed)
                  for freq, gain, decay in partials)
    return strike + ringing


def load_pcm(samples, rate):
    # 로드 후 PCM은 믹서가 보관하므로 임시 파일은 바로 정리한다.
    with TemporaryDirectory(prefix='bulbreak-sound-') as directory:
        path = Path(directory) / 'effect.wav'
        with wave.open(str(path), 'wb') as output:
            output.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
            output.writeframes(samples.tobytes())
        try:
            return load_wav(str(path))
        except IOError:
            return None
