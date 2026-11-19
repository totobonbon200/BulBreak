# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
"""고양이 제약의 MP4 영상에서 배경으로 쓸 프레임을 읽는다."""
from av import open as open_video


class LoopingVideo:
    def __init__(self, path):
        self.container = open_video(str(path))
        self.stream = self.container.streams.video[0]
