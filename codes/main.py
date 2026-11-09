
from pico2d import *
import random
from transitions import *
from pathlib import Path

from codes.maze import Maze
from codes.character import Character

GAME_OVER_OPACITY = 0.5  # 0.0: transparent, 1.0: opaque


def main():
    import pico2d as p

    root = Path(__file__).resolve().parents[1]
    maze_sheet = p.load_image(str(root / 'resources/maze_animation_sheet.png'))
    character_sheet = p.load_image(str(root / 'resources/character_animation_sheet.png'))
    font = p.load_font(str(Path('C:/Windows/Fonts/arial.ttf')), 15)
    size = random.choice((4, 6))
    completed = 0
    maze = Maze(size)
    player = Character(maze.entrance, p.get_time())
    directions = {p.SDLK_UP: (-1, 0), p.SDLK_DOWN: (1, 0),
                  p.SDLK_LEFT: (0, -1), p.SDLK_RIGHT: (0, 1)}
    held = set()
    running = True
    message = 'Arrow keys: move / hit wall twice'
    while running:
        now = p.get_time()
        player.update(now)
        transitioned = False
        for event in p.get_events():
            if event.type == p.SDL_QUIT:
                running = False
            elif event.type == p.SDL_KEYUP:
                held.discard(event.key)
            elif event.type == p.SDL_KEYDOWN and event.key in directions:
                if event.key in held:
                    continue
                held.add(event.key)
                if not player.is_playing or transitioned:
                    continue
                player.position, result = maze.step(player.position, directions[event.key])
                player.react(now)
                message = {'hit': 'Wall: 1 hit left',
                           'broken': 'Wall broken! Press again to move.',
                           'blocked': 'Map boundary',
                           'moved': 'Arrow keys: move / hit wall twice',
                           'exit': 'Next maze' }[result]
                if result == 'exit':
                    completed += 1
                    maze = Maze(size, maze.exit)
                    player.enter_maze(maze.entrance, now)
                    # Keep processing releases, but do not move in the new maze yet.
                    transitioned = True
        p.clear_canvas()
        maze.draw(maze_sheet, font, now)
        player.draw(character_sheet, maze, now)
        font.draw(100, 550, f'BulBreak | {size}x{size} | Maze {completed + 1} | {player.state.name}', (20, 20, 20))
        if player.is_playing:
            font.draw(100, 525, f'Idle time left: {player.idle_remaining(now):.1f}s', (180, 40, 40))
        else:
            message = 'GAME OVER: no action for 3 seconds'
        font.draw(100, 70, message, (20, 20, 20))
        font.draw(100, 45, 'IN: entrance / OUT: exit | Close window to quit', (20, 20, 20))
        if not player.is_playing:
            # Top row, column 4; draw over the entire scene last.
            width, height = maze_sheet.w // 4, maze_sheet.h // 2
            maze_sheet.opacify(GAME_OVER_OPACITY)
            maze_sheet.clip_draw(3 * width, height, width, height,
                                 400, 300, 800, 600)
            maze_sheet.opacify(1.0)
        p.update_canvas()
        p.delay(0.01)
