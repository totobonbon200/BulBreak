"""게임 화면의 흰색 패널과 상태 표시."""
from pico2d import draw_rectangle, fill_rectangle


def panel(left, bottom, right, top):
    fill_rectangle(left, bottom, right, top, (255, 255, 255, 128))
    draw_rectangle(left, bottom, right, top, (0, 0, 0))


def text(font, x, y, message):
    panel(x - 5, y - 12, x + len(message) * 15 + 5, y + 14)
    font.draw(x, y, message, (0, 0, 0))
