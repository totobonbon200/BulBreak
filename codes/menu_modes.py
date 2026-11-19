"""방향키로 이동하는 시작 및 안내 화면."""
# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md를 확인한다.
from pico2d import *
from sdl2 import SDL_SetTextureColorMod
from codes.constraints import CAT_CONSTRAINT, ConstraintNotice
from codes.guide_mode import GuideMode
from codes.hud import info_text, text


def draw_start_panel(image, x, y, color):
    # 오른쪽 경사는 캔버스에서 잘리고, 색상은 다른 HUD에 남기지 않는다.
    SDL_SetTextureColorMod(image.texture, *color)
    try:
        image.draw(x, y, 412, 52)
    finally:
        SDL_SetTextureColorMod(image.texture, 255, 255, 255)


def draw_panel_choice(font, image, y, label, progress, distance=24):
    # 선택 진행률에 맞춰 패널과 글자를 함께 이동시키고 글자색을 바꾼다.
    x = 663 - round(distance * progress)
    color = (255, round(255 - 35 * progress), round(255 * (1 - progress)))
    if image is not None:
        draw_start_panel(image, x, y, color)
    font.draw(x - 153, y, label, color)


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


class StartMenu(SelectionMenu):
    # 표시 문구와 선택할 모드를 같은 순서로 둔다.
    OPTIONS = (('게임시작', 'maze_mode'), ('가이드', 'guide_mode'),
               ('디버그모드', 'instrument_mode'), ('게임종료', 'quit_mode'))

    def __init__(self, font, image, menu_image):
        super().__init__(font, '', (), {})
        self.image = image
        self.menu_image = menu_image
        self.index = 0

    def confirm_selection(self):
        self.framework.change_mode(self.OPTIONS[self.index][1])

    def draw(self):
        if self.image is not None:
            scale = min(440 / self.image.w, 250 / self.image.h)
            self.image.draw(256, 465, self.image.w * scale, self.image.h * scale)
        # 네 항목을 오른쪽 아래에 쌓는다.
        for index, (label, _) in enumerate(self.OPTIONS):
            draw_panel_choice(self.font, self.menu_image, 256 - index * 63, label, index == self.index)


class GameOverMenu(SelectionMenu):
    OPTIONS = ('다시시작', '돌아가기')

    def __init__(self, start_menu, framework):
        super().__init__(start_menu.font, '', (), {})
        self.menu_image = start_menu.menu_image
        self.framework = framework
        self.index = 0

    def enter(self, first_visit):
        super().enter(first_visit)
        self.index = 0

    def confirm_selection(self):
        self.framework.resolve_game_over(restart=self.index == 0)

    def draw(self):
        for index, label in enumerate(self.OPTIONS):
            draw_panel_choice(self.font, self.menu_image, 130 - index * 63, label, index == self.index)


class ConstraintMenu(SelectionMenu):
    # 제약 선택 순서와 각 제약이 실행될 플레이 모드를 정의한다.
    OPTIONS = (('maze_mode', 'maze_arrival'), ('maze_mode', 'maze_cross'),
               ('battle_mode', 'battle_placeholder'), ('battle_mode', 'battle_rhythm'),
               ('maze_mode', CAT_CONSTRAINT), ('battle_mode', CAT_CONSTRAINT))

    def __init__(self, font):
        super().__init__(font, '디버그모드', ['위·아래: 제약 선택 / 왼쪽: 플레이 / 오른쪽: 시작 화면'],
                         {SDLK_RIGHT: 'start_mode'})
        self.index = 0
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
        super().draw()
        for index, option in enumerate(self.OPTIONS):
            label = self.option_title(*option)
            color = (255, 220, 0) if index == self.index else (255, 255, 255)
            self.font.draw(100, 390 - index * 38, label, color)
        target, self.preview.selected = self.OPTIONS[self.index]
        info_text(self.font, 100, 125, self.preview.description(target))


def create_menus(font, main_image=None, menu_image=None, *, start_font=None):
    return {
        'start_mode': StartMenu(start_font or font, main_image, menu_image),
        'guide_mode': GuideMode(font, title_font=start_font),
        'instrument_mode': ConstraintMenu(font),
        'battle_mode': MenuMode(font, 'Battle: planned',
                               ['Combat is not implemented yet.', 'LEFT: back'],
                               {SDLK_LEFT: 'start_mode'}),
        'result_mode': MenuMode(font, 'Results: planned',
                               ['Scoring is not implemented yet.', 'LEFT: back'],
                               {SDLK_LEFT: 'start_mode'}),
    }
