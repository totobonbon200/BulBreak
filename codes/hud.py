"""게임 화면의 흰색 패널과 상태 표시."""
from pico2d import draw_rectangle


def panel(left, bottom, right, top):
    draw_rectangle(left, bottom, right, top, 255, 255, 255, 128, filled=True)
    draw_rectangle(left, bottom, right, top, 0, 0, 0)


def text(font, x, y, message):
    panel(x - 5, y - 12, min(795, x + len(message) * 15 + 5), y + 14)
    font.draw(x, y, message, (0, 0, 0))


def draw_hud(assets, rules, now, completed):
    font = assets.font
    panel(100, 510, 500, 590)
    panel(520, 100, 780, 500)
    text(font, 540, 475, '제약 시스템')
    text(font, 540, 445, '현재 적용된 제약 없음')
    text(font, 530, 565, '미로 → 미로 → 전투')
    text(font, 530, 535, '진행 순서 안내 (전투 준비 중)')
