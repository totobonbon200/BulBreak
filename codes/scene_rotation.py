# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""배경을 제외한 플레이 화면의 SDL 그리기를 회전한다."""
import ctypes
from contextlib import contextmanager
from math import cos, radians, sin
from random import choice

from pico2d import pico2d as pico
import sdl2
