"""게임 화면의 흰색 패널과 상태 표시."""
# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
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
    text(font, x, y, message, size=size, background=False, dark=True)


def draw_progress(assets, current):
    for index, label in enumerate(('미로', '미로', '전투')):
        font = assets.notice_font if index == current else assets.font  # 현재 단계만 확대한다.
        info_text(font, 542 + 80 * index, 552, label)
    for x in (596, 676):
        info_text(assets.font, x, 552, '→')


def draw_timer(rules, now, paused):
    # 멈추면 남은 시간과 관계없이 막대 전체를 흰색으로 채운다.
    left, right = 542, 754
    draw_rectangle(left, 481, right, 510, 55, 55, 55, filled=True)
    fraction = 1.0 if paused else min(1.0, rules.idle_remaining(now) / rules.max_idle_time)
    color = (255, 255, 255) if paused else (255, 220, 0)
    end = left + int((right - left) * fraction)
    if end > left:
        draw_rectangle(left, 481, end, 510, *color, filled=True)

def draw_hud(assets, rules, now, completed, score=0):
    font = assets.font
    text = info_text
    assets.menu_image.draw(132, 550, 336, 90)  # 왼쪽 경사를 캔버스 밖에 둔다.
    assets.menu_image.draw(650, 345, 300, 490)
    draw_progress(assets, 2 if rules.mode == 'battle' else min(completed, 1))
    sheet = assets.effect_sheet
    width, height = sheet.w // 4, sheet.h // 2
    for index in range(3):
        column = 0 if index < rules.health else 1
        sheet.clip_draw(column * width, height, width, height,
                        64 + index * 80, 550, 64, 64)
    text(font, 375, 575, '미로 주파' if rules.mode == 'maze' else '무행동')
    text(font, 375, 550, f'{rules.idle_remaining(now):.1f}초')
    text(font, 375, 525, f'최대 {rules.max_idle_time:.2f}')
