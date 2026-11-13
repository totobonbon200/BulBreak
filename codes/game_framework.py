    # 시작모드, 설명모드, 종료모드, 미로모드, 전투모드로 전환할 코드 만들어줘
    # 이것으로 코드를 넘나들며 사용하는 형태를 만들 것
    # 이전모드를 저장해 이것으로 처음으로 전환되는지, 전환되는지 확인
    # 이곳에서는 초기화, 모드전환을 관리할 것
"""모드 초기화와 전환을 관리한다."""
from transitions import Machine
from codes.hud import text
from pico2d import get_time, SDL_KEYDOWN, SDLK_DOWN, SDLK_UP


class GameFramework:
    STAGE_LIMIT = 15.0
    TIMED_MODES = ('maze_mode', 'battle_mode')
    MODES = ('start_mode', 'instrument_mode', 'guide_mode', 'maze_mode',
             'battle_mode', 'result_mode', 'quit_mode')

    def __init__(self, modes, timeout_font=None, clock=None):
        self.modes = modes
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

    def change_mode(self, name):
        if name not in self.MODES:
            raise ValueError(name)
        if name != self.state:
            getattr(self, 'switch_to_' + name)()

    def _leave(self):
        mode = self.modes.get(self.state)
        if mode is not None:
            mode.exit()
        self.previous_mode = self.state

    def _enter(self):
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

    def handle_event(self, event):
        if self.stage_timed_out:
            if event.type == SDL_KEYDOWN:
                if event.key == SDLK_DOWN:
                    mode = self.modes[self.state]
                    mode.enter(False)
                    if isinstance(getattr(mode, 'held', None), set):
                        mode.held.add(SDLK_DOWN)
                    self.restart_stage_timer()
                elif event.key == SDLK_UP:
                    self.change_mode('start_mode')
            return
        self.modes[self.state].handle_event(event)

    def update(self, now):
        mode = self.modes[self.state]
        if self.stage_timed_out:
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

    def draw(self):
        self.modes[self.state].draw()
        if self.stage_timed_out and self.timeout_font is not None:
            text(self.timeout_font, 100, 380, '관심받고싶음? 옛다 관심', size=38)
