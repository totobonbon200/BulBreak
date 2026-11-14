"""방향만 저장하는 5칸 FIFO와 입력 기반 준비·공격 상태."""
from collections import deque
import random

from transitions import Machine
from codes.animation import Animation


class Enemy:
    DIRECTIONS = ('left', 'right', 'up', 'down')
    CAPACITY = 5

    def __init__(self, now, frame_seconds):
        self.directions = deque()
        self.refill()
        self.direction = None
        self.machine = Machine(model=self, states=['idle', 'prepare', 'attack'],
                               initial='idle', auto_transitions=False)
        self.machine.add_transition('begin_prepare', ['idle', 'attack'], 'prepare')
        self.machine.add_transition('begin_attack', 'prepare', 'attack')
        self.animation = Animation([(3, column) for column in range(4)],
                                   now, frame_seconds, loop=True)

    def refill(self):
        while len(self.directions) < self.CAPACITY:
            self.directions.append(random.choice(self.DIRECTIONS))

    def advance(self, now, frame_seconds):
        """새 입력마다 즉시 한 단계 진행하며 애니메이션 종료를 기다리지 않는다."""
        if self.state in ('idle', 'attack'):
            if not self.directions:
                self.refill()
            self.direction = self.directions[0]
            self.begin_prepare()
            columns = (0, 1)
        else:
            self.begin_attack()
            self.directions.popleft()
            if len(self.directions) == 1:
                self.refill()
            columns = (2, 3)
        row = {'left': 0, 'right': 0, 'up': 1, 'down': 2}[self.direction]
        self.animation = Animation([(row, column) for column in columns],
                                   now, frame_seconds)
        return True
