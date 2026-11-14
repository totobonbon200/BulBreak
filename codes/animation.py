"""경과 시간으로 시트 프레임을 선택한다."""


class Animation:
    def __init__(self, frames, started, frame_seconds, loop=False, first_frame_seconds=None):
        self.frames = tuple(frames)
        self.started = started
        self.frame_seconds = frame_seconds
        self.loop = loop
        self.first_frame_seconds = (frame_seconds if first_frame_seconds is None
                                    else first_frame_seconds)

    def elapsed_frames(self, now):
        elapsed = max(0.0, now - self.started)
        duration = self.first_frame_seconds + (len(self.frames) - 1) * self.frame_seconds
        if self.loop:
            elapsed %= duration
        if elapsed < self.first_frame_seconds:
            return 0
        return 1 + int((elapsed - self.first_frame_seconds) / self.frame_seconds)

    def finished(self, now):
        duration = self.first_frame_seconds + (len(self.frames) - 1) * self.frame_seconds
        return not self.loop and now - self.started >= duration

    def frame(self, now):
        index = min(self.elapsed_frames(now), len(self.frames) - 1)
        return self.frames[index]


def draw_frame(sheet, rows, columns, frame, x, y, width, height, rotation=0.0):
    """frame의 행·열은 위에서부터 세는 0 기반 좌표이다."""
    row, column = frame
    left = column * sheet.w // columns
    right = (column + 1) * sheet.w // columns
    top = row * sheet.h // rows
    bottom = (row + 1) * sheet.h // rows
    if rotation:
        sheet.clip_composite_draw(left, sheet.h - bottom, right - left, bottom - top,
                                  rotation, '', x, y, width, height)
    else:
        sheet.clip_draw(left, sheet.h - bottom, right - left, bottom - top,
                        x, y, width, height)
