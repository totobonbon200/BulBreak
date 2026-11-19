# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""배경을 제외한 플레이 화면의 SDL 그리기를 회전한다."""
import ctypes
from contextlib import contextmanager
from math import cos, radians, sin
from random import choice

from pico2d import pico2d as pico
import sdl2


class SceneRotation:
    SPEED = 45.0

    def __init__(self, now):
        # 미로 또는 전투에 들어갈 때 회전 기준을 한 번 정한다.
        self.started = now
        self.around_canvas = choice((True, False))


class RotatedDraw:
    def __init__(self, angle, canvas_center):
        self.angle = angle % 360
        self.canvas_center = canvas_center
        self.cosine, self.sine = cos(radians(self.angle)), sin(radians(self.angle))

    def point(self, x, y, pivot):
        cx, cy = self.canvas_center if self.canvas_center is not None else pivot
        dx, dy = x - cx, y - cy
        return (cx + dx * self.cosine - dy * self.sine,
                cy + dx * self.sine + dy * self.cosine)

    def copy(self, renderer, texture, source, dest):
        return self.copy_ex(renderer, texture, source, dest, 0, None, sdl2.SDL_FLIP_NONE)

    def copy_ex(self, renderer, texture, source, dest, angle, center, flip):
        # 폰트도 텍스처 복사를 사용하므로 같은 회전을 적용한다.
        pivot = dest.x + dest.w / 2, dest.y + dest.h / 2
        x, y = self.point(*pivot, pivot)
        rect = sdl2.SDL_Rect(round(x - dest.w / 2), round(y - dest.h / 2), dest.w, dest.h)
        return sdl2.SDL_RenderCopyEx(renderer, texture, source, rect, angle + self.angle, center, flip)
