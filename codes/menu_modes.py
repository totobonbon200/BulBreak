"""방향키로 이동하는 시작 및 안내 화면."""
# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
from pico2d import *
from sdl2 import SDL_SetTextureColorMod
from codes.constraints import CAT_CONSTRAINT, ConstraintNotice
from codes.hud import info_text, text


def draw_start_panel(image, x, y, color, opacity=1.0):
    # 패널을 오른쪽으로 48픽셀 늘리고, 그리기 뒤 공용 이미지의 색과 투명도를 복원한다.
    SDL_SetTextureColorMod(image.texture, *color)
    image.opacify(opacity)
    try:
        image.draw(x + 24, y, 460, 52)
    finally:
        image.opacify(1.0)
        SDL_SetTextureColorMod(image.texture, 255, 255, 255)


def draw_panel_choice(font, image, y, label, progress, rows_below, *, left=False):
    # 각 행의 간격과 선택 돌출을 화면 안쪽 방향으로 적용한다.
    offset = 8 * rows_below + round(36 * progress)
    x = -40 + offset if left else 663 - offset
    color = (255, round(255 - 35 * progress), round(255 * (1 - progress)))
    if image is not None:
        if progress < 1:
            draw_start_panel(image, x, y, (255, 255, 255))
        if progress > 0:
            draw_start_panel(image, x, y, (255, 220, 0), progress)
    font.draw(x + 64 if left else x - 153, y, label, color)


class MenuMode:
    def __init__(self, font, title, lines, routes):
        self.font = font
        self.title = title
        self.lines = lines
        self.routes = routes
        self.framework = None
        self.held = set()

    def enter(self, first_visit):
        self.held.clear()

    def exit(self):
        self.held.clear()

    def handle_event(self, event):
        if event.type == SDL_KEYUP:
            self.held.discard(event.key)
        elif event.type == SDL_KEYDOWN and event.key in self.routes:
            if event.key not in self.held:
                self.held.add(event.key)
                self.framework.change_mode(self.routes[event.key])

    def update(self, now):
        pass

    def draw(self):
        text(self.font, 100, 500, self.title)
        for index, line in enumerate(self.lines):
            text(self.font, 100, 450 - 30 * index, line)


class SelectionMenu(MenuMode):
    # 메뉴 선택 키는 한 번 누를 때마다 한 번만 처리한다.
    def handle_event(self, event):
        if event.type != SDL_KEYDOWN or event.key not in (SDLK_UP, SDLK_DOWN, SDLK_LEFT):
            return super().handle_event(event)
        if event.key not in self.held and not getattr(event, 'repeat', False):
            self.held.add(event.key)
            self.select(event.key)

    def select(self, key):
        if key == SDLK_LEFT:
            self.confirm_selection()
        else:
            step = -1 if key == SDLK_UP else 1
            self.index = (self.index + step) % len(self.OPTIONS)


class AnimatedSelectionMenu(SelectionMenu):
    def update(self, now):
        # 이미지 메뉴에서 항목별 선택·해제 전환을 0.25초 동안 진행한다.
        step = 0.0 if self.last_update is None else max(0.0, now - self.last_update) / 0.25
        self.last_update = now
        for index, progress in enumerate(self.progress):
            self.progress[index] = min(1.0, progress + step) if index == self.index else max(0.0, progress - step)


class StartMenu(AnimatedSelectionMenu):
    # 표시 문구와 선택할 모드를 같은 순서로 둔다.
    OPTIONS = (('게임시작', 'maze_mode'), ('가이드', 'guide_mode'),
               ('디버그모드', 'instrument_mode'), ('게임종료', 'quit_mode'))

    def __init__(self, font, image, menu_image):
        super().__init__(font, '', (), {})
        self.image = image
        self.menu_image = menu_image
        self.index = 0
        self.progress = [0.0] * len(self.OPTIONS)
        self.last_update = None

    def confirm_selection(self):
        self.framework.change_mode(self.OPTIONS[self.index][1])

    def draw(self):
        if self.image is not None:
            scale = min(440 / self.image.w, 250 / self.image.h)
            self.image.draw(256, 465, self.image.w * scale, self.image.h * scale)
        # 네 항목을 오른쪽 아래에 쌓는다.
        for index, (label, _) in enumerate(self.OPTIONS):
            draw_panel_choice(self.font, self.menu_image, 256 - index * 63, label, self.progress[index], 3 - index)


class GameOverMenu(AnimatedSelectionMenu):
    OPTIONS = ('다시시작', '돌아가기')

    def __init__(self, start_menu, framework):
        super().__init__(start_menu.font, '', (), {})
        self.menu_image = start_menu.menu_image
        self.framework = framework
        self.enter(False)

    def enter(self, first_visit):
        super().enter(first_visit)
        self.index = 0
        self.progress = [0.0] * len(self.OPTIONS)  # 새 게임오버마다 흰색 위치에서 시작한다.
        self.last_update = None

    def confirm_selection(self):
        self.framework.resolve_game_over(restart=self.index == 0)

    def draw(self):
        for index, label in enumerate(self.OPTIONS):
            draw_panel_choice(self.font, self.menu_image, 130 - index * 63, label, self.progress[index], 1 - index)


class ConstraintMenu(AnimatedSelectionMenu):
    # 제약 선택 순서와 각 제약이 실행될 플레이 모드를 정의한다.
    OPTIONS = (('maze_mode', 'maze_cross'),
               ('battle_mode', 'battle_placeholder'), ('battle_mode', 'battle_rhythm'),
               ('maze_mode', CAT_CONSTRAINT), ('battle_mode', CAT_CONSTRAINT),
               ('maze_mode', 'maze_darkness'), ('battle_mode', 'battle_building'),
               ('maze_mode', 'maze_bomber'))

    def __init__(self, font, menu_image=None):
        super().__init__(font, '디버그모드', ['위·아래: 제약 선택 / 왼쪽: 플레이 / 오른쪽: 시작 화면'],
                         {SDLK_RIGHT: 'start_mode'})
        self.index = 0
        self.menu_image = menu_image
        self.progress = [0.0] * len(self.OPTIONS)  # 디버그 목록도 항목별 선택 진행률을 관리한다.
        self.last_update = None
        self.preview = ConstraintNotice()  # 실제 플레이와 같은 이름과 설명을 표시한다.

    def confirm_selection(self):
        self.framework.play_constraint(*self.OPTIONS[self.index])

    def option_title(self, target, key):
        # 같은 고양이 제약도 실행할 모드에 따라 구분한다.
        self.preview.selected = key
        title = self.preview.title()
        if key != CAT_CONSTRAINT:
            return title
        mode = '미로' if target == 'maze_mode' else '전투'
        return f'[{mode}] {title}'

    def draw(self):
        info_text(self.font, 24, 550, self.title)
        info_text(self.font, 320, 500, self.lines[0])
        for index, option in enumerate(self.OPTIONS):
            label = self.option_title(*option)
            draw_panel_choice(self.font, self.menu_image, 480 - index * 58, label,
                              self.progress[index], len(self.OPTIONS) - 1 - index, left=True)
        target, self.preview.selected = self.OPTIONS[self.index]
        info_text(self.font, 320, 430, self.preview.description(target))


def create_menus(font, main_image=None, menu_image=None, *, start_font=None):
    from codes.guide_mode import GuideMode  # 가이드는 이 모듈의 공통 메뉴를 사용한다.
    return {
        'start_mode': StartMenu(start_font or font, main_image, menu_image),
        'guide_mode': GuideMode(font, title_font=start_font, menu_image=menu_image),
        'instrument_mode': ConstraintMenu(font, menu_image),
        'battle_mode': MenuMode(font, 'Battle: planned',
                               ['Combat is not implemented yet.', 'LEFT: back'],
                               {SDLK_LEFT: 'start_mode'}),
        'result_mode': MenuMode(font, 'Results: planned',
                               ['Scoring is not implemented yet.', 'LEFT: back'],
                               {SDLK_LEFT: 'start_mode'}),
    }
