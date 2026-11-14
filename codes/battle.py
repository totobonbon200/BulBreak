"""15초 제한의 임시 전투: 실시간 입력과 적의 방향 FIFO를 연결한다."""
from pico2d import *
import math
from transitions import Machine

from codes.animation import Animation, draw_frame
from codes.enemy import Enemy
from codes.gameover import GameOverRules
from codes.hud import draw_hud, info_text as text


class BattleMode:
    DIRECTIONS = {SDLK_LEFT: 'left', SDLK_RIGHT: 'right',
                  SDLK_UP: 'up', SDLK_DOWN: 'down'}
    CLEAR_ATTACKS = 10
    FAILURE_SECONDS = 0.6
    FAILURE_EFFECT_SECONDS = 0.4

    def __init__(self, assets):
        self.assets = assets
        self.held = set()
        self.pending_session = None
        self.machine = Machine(model=self,
                               states=['idle', 'attack', 'parry', 'dodge_up',
                                       'dodge_down', 'hit'],
                               initial='idle', model_attribute='player_state',
                               auto_transitions=False)
        for state in ('idle', 'attack', 'parry', 'dodge_up', 'dodge_down', 'hit'):
            self.machine.add_transition('show_' + state, '*', state)

    def enter(self, first_visit):
        self.now = get_time()
        self.held.clear()
        if self.pending_session is None:
            self.rules, self.score = GameOverRules(self.now), 0
        else:
            self.rules, self.score = self.pending_session
            self.pending_session = None
        self.rules.enter_battle(self.now)
        self.rules.remaining = self.rules.max_idle_time
        self.successes = 0
        self.next_attack_direction = 'left'
        self.failure_started = None
        self.stage_timed_out = False
        self.cleared = False
        self.enemy = Enemy(self.now, self.rules.animation_frame_seconds)
        self.show_idle()
        self.visual_state = 'idle'
        self.player_direction = 'right'
        self.player_animation = self.make_player_animation('idle', 'right')
        self.player_effect = None
        self.enemy_effect = None
        self.message = '임시 전투: 올바른 좌우 공격 10회 성공'

    def exit(self):
        self.held.clear()

    @property
    def is_game_over(self):
        return self.rules.is_over

    def on_stage_timeout(self):
        self.stage_timed_out = True
        self.rules.health = 0

    def make_player_animation(self, state, direction):
        if state in ('attack', 'parry'):
            row = 0 if direction == 'left' else 1
            frames = [(row, column) for column in range(4)]
        elif state == 'hit':
            frames = [(0, 2), (0, 3)]
        elif state in ('dodge_up', 'dodge_down'):
            columns = (0, 1) if state == 'dodge_up' else (2, 3)
            frames = [(1, column) for column in columns]
        else:
            row = 2 if direction == 'left' else 3
            frames = [(row, column) for column in range(4)]
        return Animation(frames, self.now, self.rules.animation_frame_seconds,
                         loop=state == 'idle')

    def display_action(self, state, direction):
        getattr(self, 'show_' + state)()
        self.visual_state = state
        self.player_direction = direction
        self.player_animation = self.make_player_animation(state, direction)

    def start_effect(self, owner):
        columns = (0, 1) if owner == 'player' else (2, 3)
        setattr(self, owner + '_effect', Animation(
            [(0, column) for column in columns], self.now,
            self.rules.animation_frame_seconds))

    def show_failure(self):
        self.failure_started = self.now

    def failure_rotation(self):
        if self.failure_started is None:
            return 0.0
        progress = (self.now - self.failure_started) / self.FAILURE_SECONDS
        if not 0.0 < progress < 1.0:
            return 0.0
        return -math.radians(15) * math.sin(math.pi * progress) ** 2

    def handle_event(self, event):
        if event.type == SDL_KEYUP:
            self.held.discard(event.key)
            return
        if event.type != SDL_KEYDOWN or event.key not in self.DIRECTIONS:
            return
        if getattr(event, 'repeat', False):
            return
        if event.key in self.held:
            return
        self.held.add(event.key)
        if self.is_game_over:
            if event.key == SDLK_DOWN:
                self.enter(False)
                self.held.add(SDLK_DOWN)
                self.framework.restart_stage_timer()
            elif event.key == SDLK_UP:
                self.framework.change_mode('start_mode')
            return
        if self.cleared:
            return
        self.rules.record_action(self.now)
        if self.is_game_over:
            return

        direction = self.DIRECTIONS[event.key]
        advanced = self.enemy.advance(self.now, self.rules.animation_frame_seconds)
        expected = self.enemy.direction
        correct = direction == expected
        enemy_attacking = advanced and self.enemy.state == 'attack'
        attack_order_correct = direction == self.next_attack_direction

        if direction in ('left', 'right'):
            self.start_effect('player')
            if attack_order_correct:
                self.successes += 1
                self.next_attack_direction = 'right' if direction == 'left' else 'left'
                self.message = f'공격 성공: {self.successes}/{self.CLEAR_ATTACKS}'
            else:
                self.show_failure()
                self.message = '공격 순서 실패: 노란 화살표 방향으로 공격'
            self.display_action('parry' if correct and enemy_attacking else 'attack', direction)
        else:
            self.display_action('dodge_' + direction, direction)
            self.message = '회피 성공' if correct else '회피 방향 불일치'

        if enemy_attacking:
            self.start_effect('enemy')
            if not correct:
                self.rules.record_wrong_defense()
                self.show_failure()
                horizontal_order_failure = (expected in ('left', 'right')
                                            and direction in ('left', 'right')
                                            and not attack_order_correct)
                if not horizontal_order_failure:
                    self.display_action('hit', direction)
                self.message = '피격! 타이머 0.5초 감소'

        if self.successes >= self.CLEAR_ATTACKS and not self.is_game_over:
            self.cleared = True
            maze = self.framework.modes['maze_mode']
            maze.pending_session = (self.rules, self.score)
            self.framework.change_mode('maze_mode')

    def update(self, now):
        self.now = now
        if self.is_game_over or self.cleared:
            return
        self.rules.update(now)
        if self.player_animation.finished(now):
            self.show_idle()
            self.visual_state = 'idle'
            self.player_animation = self.make_player_animation('idle', self.player_direction)

    def draw(self):
        draw_frame(self.assets.enemy_sheet, 4, 4, self.enemy.animation.frame(self.now),
                   350, 360, 150, 150)
        if self.enemy.state == 'prepare':
            column = ('left', 'right', 'up', 'down').index(self.enemy.direction)
            draw_frame(self.assets.effect_sheet, 2, 4, (1, column),
                       350, 465, 65, 65)
        attack_sheet = self.visual_state in ('attack', 'parry')
        sheet = self.assets.character_attack_sheet if attack_sheet else self.assets.character_sheet
        draw_frame(sheet, 2 if attack_sheet else 4, 4,
                   self.player_animation.frame(self.now), 240, 200, 130, 130,
                   rotation=self.failure_rotation())
        arrow_sheet = self.assets.yellow_arrow_sheet
        # 원본 생성 시트의 셀 종횡비를 보존해 화살표가 찌그러지지 않게 한다.
        arrow_height = 65 * arrow_sheet.h / (arrow_sheet.w / 4)
        column = 0 if self.next_attack_direction == 'left' else 1
        draw_frame(arrow_sheet, 1, 4, (0, column), 240, 295, 65, arrow_height)
        if (self.failure_started is not None
                and 0 <= self.now - self.failure_started < self.FAILURE_EFFECT_SECONDS):
            draw_frame(self.assets.effect_sheet, 2, 4, (0, 1), 240, 230, 65, 65)
        for owner, position in (('player', (310, 260)), ('enemy', (310, 300))):
            effect = getattr(self, owner + '_effect')
            if effect is not None and not effect.finished(self.now):
                draw_frame(self.assets.effect_attack_sheet, 1, 4, effect.frame(self.now),
                           *position, 110, 110)
        draw_hud(self.assets, self.rules, self.now, 2, self.score)
        text(self.assets.font, 100, 85, f'공격 성공: {self.successes}/{self.CLEAR_ATTACKS}')
        text(self.assets.font, 100, 60, self.message)
        text(self.assets.font, 100, 35, '좌→우 교대 공격 / 상하: 회피 / 노란 화살표: 다음 공격')
        if self.is_game_over:
            sheet = self.assets.maze_sheet
            sheet.opacify(0.5)
            try:
                draw_frame(sheet, 2, 4, (0, 3), 400, 300, 800, 600)
            finally:
                sheet.opacify(1.0)
            text(self.assets.font, 180, 320, '아래: 재시작 / 위: 시작 화면')
