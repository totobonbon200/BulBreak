"""모드 초기화와 전환을 관리한다."""
from transitions import Machine


class GameFramework:
    MODES = ('start_mode', 'instrument_mode', 'guide_mode', 'maze_mode',
             'battle_mode', 'result_mode', 'quit_mode')

    def __init__(self, modes):
        self.modes = modes
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
        if self.state == 'quit_mode':
            self.running = False
            return
        mode = self.modes[self.state]
        first_visit = self.state not in self.visited
        mode.enter(first_visit)
        self.visited.add(self.state)

    def handle_event(self, event):
        self.modes[self.state].handle_event(event)

    def update(self, now):
        self.modes[self.state].update(now)

    def draw(self):
        self.modes[self.state].draw()
