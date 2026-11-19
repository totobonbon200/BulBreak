# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""고양이 제약의 MP4 영상에서 배경으로 쓸 프레임을 읽는다."""
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
