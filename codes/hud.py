"""게임 화면의 흰색 패널과 상태 표시."""
from pico2d import draw_rectangle


def panel(left, bottom, right, top):
    draw_rectangle(left, bottom, right, top, 255, 255, 255, 128, filled=True)
    draw_rectangle(left, bottom, right, top, 0, 0, 0)


def text(font, x, y, message, size=15, background=True):
    if background:
        width = sum(size if ord(char) > 127 else size * 0.6 for char in message)
        panel(x - 5, y - size * 0.6 - 3, min(795, x + width + 5), y + size * 0.6 + 3)
    font.draw(x, y, message, (0, 0, 0))


def game_text(font, x, y, message, size=15):
    text(font, x, y, message, size=size, background=False)


def draw_hud(assets, rules, now, completed, score=0):
    font = assets.font
    game_text(font, 640, 575, f'점수: {score}')
    game_text(font, 530, 535, '미로 → 미로 → 전투')
    sheet = assets.effect_sheet
    width, height = sheet.w // 4, sheet.h // 2
    for index in range(3):
        column = 0 if index < rules.health else 1
        sheet.clip_draw(column * width, height, width, height,
                        145 + index * 85, 550, 64, 64)
    text(font, 375, 575, '무행동')
    text(font, 375, 550, f'{rules.idle_remaining(now):.1f}초')
    text(font, 375, 525, f'최대 {rules.max_idle_time:.2f}')
    text(font, 540, 410, f'현재 미로: {completed + 1}')
