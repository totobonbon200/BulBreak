# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md의 최신 기준을 확인한다.
    # 시작모드, 설명모드, 종료모드, 미로모드, 전투모드로 전환할 코드 만들어줘
    # 이것으로 코드를 넘나들며 사용하는 형태를 만들 것
    # 이전모드를 저장해 이것으로 처음으로 전환되는지, 전환되는지 확인
    # 이곳에서는 초기화, 모드전환을 관리할 것
"""모드 초기화와 전환을 관리한다."""
from transitions import Machine
from codes.constraints import CAT_CONSTRAINT, ConstraintNotice
from codes.hud import info_text as text
from codes.menu_modes import GameOverMenu
from pico2d import get_time


class GameFramework:
    STAGE_LIMIT = 15.0
    TIMED_MODES = ('maze_mode', 'battle_mode')
    MODES = ('start_mode', 'instrument_mode', 'guide_mode', 'maze_mode',
             'battle_mode', 'tutorial_mode', 'result_mode', 'quit_mode')

    def __init__(self, modes, timeout_font=None, clock=None, cat_effect=None):
        self.notice = ConstraintNotice()  # 전환 안내와 일반 진행을 분리한다.
        self.cat_effect = cat_effect
        self.modes = modes
        self.game_over_menu = GameOverMenu(modes['start_mode'], self)
        self.clock = clock or get_time
        self.timeout_font = timeout_font
        self.stage_started = None
        self.stage_elapsed = 0.0
        self.stage_timed_out = False
        self.previous_mode = None
        self.visited = set()
        self.running = True
        self.machine = Machine(model=self, states=self.MODES,
                               initial='start_mode', auto_transitions=False)
        for name in self.MODES:
            self.machine.add_transition('switch_to_' + name, '*', name,
                                        before='_leave', after='_enter')
        self._enter()

    @property
    def current_mode(self):
        return self.state

    @property
    def timer_paused(self):
        return self.state == 'tutorial_mode' or self.stage_timed_out or self.notice.pending is not None

    @property
    def game_over_active(self):
        return self.stage_timed_out or getattr(self.modes[self.state], 'is_game_over', False) is True

    def change_mode(self, name):
        if name not in self.MODES:
            raise ValueError(name)
        tutorial = self.modes.get('tutorial_mode')
        if name == 'maze_mode' and self.state == 'start_mode' and getattr(tutorial, 'completed', True) is False:
            name = 'tutorial_mode'
        if name == 'instrument_mode' or (name == 'maze_mode' and self.state not in self.TIMED_MODES):
            self.notice.reset()
        if self.notice.begin(self.state, name, self.clock()):
            return
        self._change_mode(name)

    def _change_mode(self, name):
        if name != self.state:
            getattr(self, 'switch_to_' + name)()

    @property
    def practicing_constraint(self):
        return self.previous_mode == 'instrument_mode' and self.state in self.TIMED_MODES

    def play_constraint(self, target, key):
        self.notice.reset()  # 선택한 제약만 적용한 뒤 새 판을 초기화한다.
        self.notice.selected = key
        self.notice.active = {key}
        self._change_mode(target)

    def _leave(self):
        mode = self.modes.get(self.state)
        if mode is not None:
            mode.exit()
        self.previous_mode = self.state

    def _enter(self):
        self.game_over_menu.enter(False)
        self.stage_started = None
        self.stage_elapsed = 0.0
        self.stage_timed_out = False
        if self.state == 'quit_mode':
            self.running = False
            return
        mode = self.modes[self.state]
        first_visit = self.state not in self.visited
        mode.enter(first_visit)
        self.restart_stage_timer()
        self.visited.add(self.state)

    def restart_stage_timer(self):
        """Start a fresh deadline on maze/battle entry, never on ordinary input."""
        self.stage_started = self.clock() if self.state in self.TIMED_MODES else None
        self.stage_elapsed = 0.0
        self.stage_timed_out = False

    def resolve_game_over(self, restart):
        if not restart:
            self.change_mode('instrument_mode' if self.practicing_constraint else 'start_mode')
            return
        if not self.practicing_constraint:
            self.notice.reset()
        self.modes[self.state].enter(False)
        self.restart_stage_timer()
        self.game_over_menu.enter(False)

    def handle_event(self, event):
        if self.notice.pending is not None:
            return  # 안내 중 방향키는 다음 플레이에 전달하지 않는다.
        if self.game_over_active:
            self.game_over_menu.handle_event(event)
            return
        self.modes[self.state].handle_event(event)

    def update(self, now):
        if self.notice.pending is not None:
            target = self.notice.finish(now)
            if target is not None:
                self._change_mode(target)
            return  # 안내 중에는 일반 타이머와 적 큐를 진행하지 않는다.
        if self.game_over_active:
            self.game_over_menu.update(now)
            return  # 게임오버 중에는 메뉴의 선택 전환만 진행한다.
        mode = self.modes[self.state]
        if getattr(mode, 'awaiting_next_maze', False) is True:
            return  # 도착 확인 대기에는 일반 게임오버 타이머를 진행하지 않는다.
        # 리듬 제약은 체력 판정만 진행하며 독립 제한 시계도 멈춘다.
        if 'battle_rhythm' in self.notice.active and self.state == 'battle_mode':
            mode.update(now)
            return
        if self.stage_started is not None and getattr(mode, 'is_game_over', False) is not True:
            self.stage_elapsed = min(self.STAGE_LIMIT, max(0.0, now - self.stage_started))
            if self.stage_elapsed >= self.STAGE_LIMIT:
                self.stage_timed_out = True
                callback = getattr(mode, 'on_stage_timeout', None)
                if callback is not None:
                    callback()
                return
        mode.update(now)

    def _active_cat_effect(self, now):
        # 전환 안내와 메뉴에서는 효과를 지우고 새 적용을 기다린다.
        active = (self.state in self.TIMED_MODES and self.notice.pending is None
                  and CAT_CONSTRAINT in self.notice.active)
        if self.cat_effect is not None and self.cat_effect.sync(active, now):
            return self.cat_effect

    def draw(self):
        if self.state == 'tutorial_mode':
            self.modes[self.state].draw()
            return  # 튜토리얼이 강조 표시와 고양이 연출을 직접 그린다.
        now = self.clock()
        cats = self._active_cat_effect(now)
        if cats is not None:
            cats.draw_background(now)
        self.modes[self.state].draw()
        if cats is not None:
            cats.draw_cats(now)
        if self.notice.pending is not None:
            self.notice.draw(self.modes[self.state].assets.notice_font)
        if self.stage_timed_out and self.timeout_font is not None:
            text(self.timeout_font, 100, 380, '관심받고싶음? 옛다 관심', size=38)
        if self.game_over_active:
            self.game_over_menu.draw()
