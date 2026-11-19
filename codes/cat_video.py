# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""고양이 제약의 MP4 영상에서 배경으로 쓸 프레임을 읽는다."""
from itertools import islice
from av import open as open_video
from pico2d import Image, draw_rectangle
from sdl2 import (SDL_CreateTexture, SDL_GetError, SDL_PIXELFORMAT_RGB24,
                  SDL_TEXTUREACCESS_STREAMING, SDL_UpdateTexture)


class LoopingVideo:
    def __init__(self, path):
        self.container = open_video(str(path))
        self.stream = self.container.streams.video[0]
        # 원본의 절반 크기인 텍스처 한 장을 프레임마다 갱신한다.
        renderer = draw_rectangle.__globals__['renderer']
        texture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGB24, SDL_TEXTUREACCESS_STREAMING,
                                    self.stream.width // 2, self.stream.height // 2)
        if not texture:
            raise RuntimeError(SDL_GetError().decode())
        self.image = Image(texture)
        self.index, self.frames = -1, self.container.decode(self.stream)

    def frame_at(self, elapsed):
        # 일정한 프레임 간격의 원본 영상은 마지막 프레임 뒤에 처음으로 돌아간다.
        index = int(elapsed * self.stream.average_rate) % self.stream.frames
        if index < self.index:
            self.container.seek(0, stream=self.stream)
            self.index, self.frames = -1, self.container.decode(self.stream)
        if index != self.index:
            frame = next(islice(self.frames, index - self.index - 1, None))
            self.index = index
            return frame

    def advance(self, elapsed):
        # 프레임이 바뀌면 배경 텍스처에 영상 픽셀을 올린다.
        frame = self.frame_at(elapsed)
        if frame is not None:
            rgb = frame.reformat(width=self.image.w, height=self.image.h, format='rgb24')
            plane = rgb.planes[0]
            if SDL_UpdateTexture(self.image.texture, None, plane.buffer_ptr, plane.line_size) != 0:
                raise RuntimeError(SDL_GetError().decode())
