"""15초 제한의 임시 전투: 실시간 입력과 적의 방향 FIFO를 연결한다."""
# 작업 전 ppt/AI_Planner.md와 ppt/Code_Plans.md의 최신 작성·커밋 기준을 확인한다.
# 입력 판정과 표시를 연결한다. 코드 커밋은 관련 파일 3개·변경 10줄 이내로 나눈다.
from pico2d import *
import math
from transitions import Machine

from codes.animation import Animation, draw_frame
from codes.building_battle import BuildingBattle
from codes.clap_sound import play_go_sound
from codes.enemy import Enemy
from codes.rhythm import Rhythm
from codes.rhythm_countdown import RhythmCountdown, draw_countdown_text
from codes.gameover import GameOverRules
from codes.hud import draw_enemy_health, draw_hud


class BattleMode:
    DIRECTIONS = {SDLK_LEFT: 'left', SDLK_RIGHT: 'right',
                  SDLK_UP: 'up', SDLK_DOWN: 'down'}
    CLEAR_ATTACKS = 10
    FAILURE_SECONDS = 0.6
    FAILURE_EFFECT_SECONDS = 0.4

    def __init__(self, assets):
        self.assets = assets
        self.held = set()
        self.countdown = None
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
        # 무효과 제약은 유지하고 새 리듬 제약이 있을 때만 판정한다.
        active = getattr(getattr(self.framework, 'notice', None), 'active', set())
        self.countdown = RhythmCountdown(self.now) if isinstance(active, set) and 'battle_rhythm' in active else None
        self.rhythm = Rhythm(self.countdown.end) if self.countdown is not None else None
        self.building = (BuildingBattle(self.now)
                         if isinstance(active, set) and 'battle_building' in active else None)
        # 리듬은 원본 전체 박자 수를 목표로 삼고 일반 전투 진입 시 10회로 복구한다.
        self.CLEAR_ATTACKS = (sum(map(len, self.rhythm.patterns)) if self.rhythm
                              else type(self).CLEAR_ATTACKS)
        if self.building is not None:
            self.CLEAR_ATTACKS = self.building.floors * self.building.HITS_PER_FLOOR
        self.successes = 0
        self.next_attack_direction = 'left'
        self.failure_started = None
        self.horizontal_attack_parry = False
        self.stage_timed_out = False
        self.cleared = False
        self.enemy = Enemy(self.now, self.rules.animation_frame_seconds)
        self.show_idle()
        self.visual_state = 'idle'
        self.player_direction = 'right'
        self.player_animation = self.make_player_animation('idle', 'right')
        self.player_effect = None
        self.enemy_effect = None
        self.message = f'전투 목표: {self.CLEAR_ATTACKS}회 성공'

    def exit(self):
        self.held.clear()

    @property
    def is_game_over(self):
        return self.rules.is_over

    def on_stage_timeout(self):
        self.stage_timed_out = True
        self.rules.health = 0

    def make_player_animation(self, state, direction):
        # 가로공격 대응도 누른 방향의 공격 시트 행을 재생한다.
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
        self.player_animation = self.make_player_animation(self.visual_state, direction)

    def start_effect(self, owner):
        columns = (0, 1) if owner == 'player' else (2, 3)
        setattr(self, owner + '_effect', Animation(
            [(0, column) for column in columns], self.now,
            self.rules.animation_frame_seconds))

    def show_failure(self):
        self.failure_started = self.now

    def failure_rotation(self):
        if self.failure_started is None or self.horizontal_attack_parry:
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
        if self.building is not None:
            self.handle_building(event.key)
            return
        if self.rhythm is not None:
            self.now = get_time()  # 프레임 시각 대신 실제 입력 시각을 사용한다.
            self.update_rhythm(self.now)
            if self.countdown is not None and self.now < self.countdown.end:
                return
            if self.is_game_over:
                return
            if self.rhythm.index == len(self.rhythm.hits):
                return  # 입력을 마친 뒤 다음 시범을 기다리는 동안에는 피해가 없다.
            if (self.now < self.rhythm.started + 2
                    and self.now < self.rhythm.beat_times()[0] - self.rhythm.WINDOW):
                return  # 첫 입력 박자의 이른 허용 범위를 보존한다.
            if not self.rhythm.press(self.now):
                self.rules.health = max(0, self.rules.health - 1)
                self.message = '박자 실패! 체력 1 감소'
                return
        else:
            self.rules.record_action(self.now)
        if self.is_game_over:
            return

        direction = self.DIRECTIONS[event.key]
        # 리듬 성공은 누른 방향과 관계없이 다음 교대 공격으로 연결한다.
        if self.rhythm is not None:
            direction = self.next_attack_direction
        advanced = self.enemy.advance(self.now, self.rules.animation_frame_seconds)
        expected = self.enemy.direction
        correct = direction == expected
        if self.rhythm is not None:
            correct = True  # 리듬 제약의 피해는 박자 실패·누락으로만 판정한다.
        enemy_attacking = advanced and self.enemy.state == 'attack'
        attack_order_correct = direction == self.next_attack_direction
        self.horizontal_attack_parry = (enemy_attacking
                                        and expected in ('left', 'right')
                                        and direction in ('left', 'right'))
        # 적 가로공격에는 좌우 입력 모두 성공하며 이전 실패 표시도 해제한다.
        if self.horizontal_attack_parry:
            correct = attack_order_correct = True
            self.failure_started = None

        if direction in ('left', 'right'):
            if attack_order_correct:
                self.start_effect('player')
                self.successes += 1
                if self.rhythm is not None:
                    self.rhythm.take_next_pattern_cue(self.now)  # 전환 시각은 기록하고 타격음은 생략한다.
                else:
                    play_go_sound(self.assets)
                self.next_attack_direction = 'right' if direction == 'left' else 'left'
                self.message = f'공격 성공: {self.successes}/{self.CLEAR_ATTACKS}'
            else:
                self.player_effect = None
                self.show_failure()
                self.message = '공격 순서 실패: 노란 화살표 방향으로 공격'
            state = 'idle'
            if attack_order_correct:
                state = 'parry' if correct and enemy_attacking else 'attack'
            self.display_action(state, direction)
        else:
            self.display_action('dodge_' + direction, direction)
            self.message = '회피 성공' if correct else '회피 방향 불일치'

        if enemy_attacking:
            self.start_effect('enemy')
            if not correct:
                vertical_hit = expected in ('up', 'down')
                if self.rhythm is None:
                    self.rules.record_wrong_defense(health_damage=1 if vertical_hit else 0)
                elif vertical_hit:
                    self.rules.health = max(0, self.rules.health - 1)
                self.show_failure()
                horizontal_order_failure = (expected in ('left', 'right')
                                            and direction in ('left', 'right')
                                            and not attack_order_correct)
                if not horizontal_order_failure:
                    self.display_action('hit', direction)
                self.message = ('피격! 체력 1 감소·타이머 0.5초 차감' if vertical_hit
                                else '피격! 타이머 0.5초 감소')
                if self.rhythm is not None:
                    self.message = '피격! 체력 1 감소' if vertical_hit else '방어 방향 불일치'

        self.finish_if_cleared()

    def handle_building(self, key):
        # 좌우 입력은 교대 순서 없이 닿아 있는 건물을 공격한다.
        if key == SDLK_DOWN:
            return
        self.rules.record_action(self.now)
        if key == SDLK_UP and not self.is_game_over and self.building.jump():
            self.display_action('dodge_up', self.player_direction)
        if not self.is_game_over and key in (SDLK_LEFT, SDLK_RIGHT) and self.building.attack():
            self.successes += 1
            self.display_action('attack', self.DIRECTIONS[key])
            self.finish_if_cleared()

    def finish_if_cleared(self):
        # 일반 공격과 건물 타격이 같은 완료 흐름을 사용한다.
        if self.successes >= self.CLEAR_ATTACKS and not self.is_game_over:
            self.cleared = True
            # 제약 한 판의 전투를 마치면 선택 화면으로 돌아간다.
            if getattr(self.framework, 'practicing_constraint', False) is True:
                self.framework.change_mode('instrument_mode')
                return
            maze = self.framework.modes['maze_mode']
            maze.pending_session = (self.rules, self.score)
            self.framework.change_mode('maze_mode')

    def update(self, now):
        self.now = now
        if self.is_game_over or self.cleared:
            return
        if self.rhythm is not None:
            self.update_rhythm(now)
        else:
            self.rules.update(now)
        if self.building is not None:
            self.building.update(now)
        if self.player_animation.finished(now):
            self.show_idle()
            self.visual_state = 'idle'
            self.player_animation = self.make_player_animation('idle', self.player_direction)

    def draw_player(self, x, y, size):
        # 일반 전투와 건물부수기가 같은 주인공 애니메이션을 그린다.
        attacking = self.visual_state in ('attack', 'parry')
        sheet = self.assets.character_attack_sheet if attacking else self.assets.character_sheet
        draw_frame(sheet, 2 if attacking else 4, 4, self.player_animation.frame(self.now),
                   x, y, size, size, rotation=self.failure_rotation())

    def draw(self):
        draw_frame(self.assets.enemy_sheet, 4, 4, self.enemy.animation.frame(self.now),
                   350, 360, 150, 150)
        if self.enemy.state == 'prepare':
            column = ('left', 'right', 'up', 'down').index(self.enemy.direction)
            draw_frame(self.assets.effect_sheet, 2, 4, (1, column),
                       350, 465, 65, 65)
        player_x, player_y = 240, 200
        self.draw_player(player_x, player_y, 130)
        arrow_sheet = self.assets.yellow_arrow_sheet
        # 원본 생성 시트의 셀 종횡비를 보존해 화살표가 찌그러지지 않게 한다.
        arrow_height = 65 * arrow_sheet.h / (arrow_sheet.w / 4)
        column = 0 if self.next_attack_direction == 'left' else 1
        # 다음 공격 방향과 같은 쪽에 주인공과 간격을 두고 표시한다.
        arrow_x = player_x + (-101 if column == 0 else 101)
        draw_frame(arrow_sheet, 1, 4, (0, column), arrow_x, player_y, 65, arrow_height)
        if (self.failure_started is not None
                and 0 <= self.now - self.failure_started < self.FAILURE_EFFECT_SECONDS):
            draw_frame(self.assets.effect_sheet, 2, 4, (0, 1), 240, 230, 65, 65)
        for owner, position in (('player', (310, 260)), ('enemy', (310, 300))):
            effect = getattr(self, owner + '_effect')
            if effect is not None and not effect.finished(self.now):
                draw_frame(self.assets.effect_attack_sheet, 1, 4, effect.frame(self.now),
                           *position, 110, 110)
        paused = self.rhythm is not None or self.cleared or self.framework.timer_paused is True
        draw_hud(self.assets, self.rules, self.now, 2, timer_paused=paused)
        draw_enemy_health(self.CLEAR_ATTACKS - self.successes, self.CLEAR_ATTACKS)
        if self.countdown is not None:
            frame = self.countdown.frame(self.now)
            if frame is not None:
                draw_countdown_text(self.assets.timeout_font, *frame)
        if self.is_game_over:
            sheet = self.assets.maze_sheet
            sheet.opacify(0.5)
            try:
                draw_frame(sheet, 2, 4, (0, 3), 400, 300, 800, 600)
            finally:
                sheet.opacify(1.0)

    def play_pattern_cue(self, now):
        if not self.is_game_over and self.rhythm.take_next_pattern_cue(now):
            play_go_sound(self.assets)

    def update_rhythm(self, now):
        # 누락 피해는 한 번만 반영하고 일반 게임오버 시계를 고정한다.
        self.rules.last_update = now
        if self.countdown is not None and now < self.countdown.end:
            self.countdown.play_go(now, getattr(self.assets, 'go_sound', None))
            return
        self.rules.health = max(0, self.rules.health - self.rhythm.advance(now))
        self.play_pattern_cue(now)
        self.rhythm.play_claps(now, getattr(self.assets, 'clap_sound', None))
        self.enemy.animation = Animation([self.rhythm.frame(now)], now, .15)
        self.message = self.rhythm.description(now)
