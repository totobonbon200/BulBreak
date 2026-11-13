"""게임 화면의 흰색 패널과 상태 표시."""
from pico2d import draw_rectangle


def panel(left, bottom, right, top, dark=False, outline=True):
    color = (0, 0, 0, 255) if dark else (255, 255, 255, 128)
    draw_rectangle(left, bottom, right, top, *color, filled=True)
    border = (255, 255, 255) if dark else (0, 0, 0)
    if outline:
        draw_rectangle(left, bottom, right, top, *border)


def text(font, x, y, message, size=15, background=True, dark=False):
    if background:
        width = sum(size if ord(char) > 127 else size * 0.6 for char in message)
        panel(x - 5, y - size * 0.6 - 3, min(795, x + width + 5), y + size * 0.6 + 3, dark=dark, outline=False)
    font.draw(x, y, message, (255, 255, 255) if dark else (0, 0, 0))


def game_text(font, x, y, message, size=15):
    text(font, x, y, message, size=size, background=False)


def info_text(font, x, y, message, size=15):
    text(font, x, y, message, size=size, dark=True)


def draw_hud(assets, rules, now, completed, score=0):
    font = assets.font
    text = info_text
    panel(100, 510, 500, 590, dark=True)
    panel(520, 510, 780, 590, dark=True)
    panel(520, 100, 780, 500, dark=True)
    text(font, 540, 475, '제약 시스템')
    text(font, 640, 575, f'점수: {score}')
    text(font, 530, 535, '미로 → 미로 → 전투')
    sheet = assets.effect_sheet
    width, height = sheet.w // 4, sheet.h // 2
    for index in range(3):
        column = 0 if index < rules.health else 1
        sheet.clip_draw(column * width, height, width, height,
                        145 + index * 85, 550, 64, 64)
    text(font, 375, 575, '무행동')
    text(font, 375, 550, f'{rules.idle_remaining(now):.1f}초')
    text(font, 375, 525, f'최대 {rules.max_idle_time:.2f}')
