"""경과 시간으로 시트 프레임을 선택한다."""


class Animation:
    def __init__(self, frames, started, frame_seconds, loop=False):
        self.frames = tuple(frames)
        self.started = started
        self.frame_seconds = frame_seconds
        self.loop = loop

    def finished(self, now):
        return not self.loop and now - self.started >= len(self.frames) * self.frame_seconds

    def frame(self, now):
        index = int(max(0.0, now - self.started) / self.frame_seconds)
        index = index % len(self.frames) if self.loop else min(index, len(self.frames) - 1)
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
