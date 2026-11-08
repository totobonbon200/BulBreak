"""Run with: py BulBreak.py (requires pico2d)."""
import random
from pathlib import Path

from codes.maze import Maze
from codes.character import Character

def main():
    import pico2d as p

    p.open_canvas(800, 600)
    try:
        root = Path(__file__).resolve().parent
        maze_sheet = p.load_image(str(root / 'resources/maze_animation_sheet.png'))
        character_sheet = p.load_image(str(root / 'resources/character_animation_sheet.png'))
        font = p.load_font(str(Path('C:/Windows/Fonts/arial.ttf')), 15)
        size = random.choice((4, 6))
        total = 3 if size == 4 else 2
        completed = 0
        maze = Maze(size)
        player = Character(maze.entrance)
        directions = {p.SDLK_UP: (-1, 0), p.SDLK_DOWN: (1, 0),
                      p.SDLK_LEFT: (0, -1), p.SDLK_RIGHT: (0, 1)}
        held = set()
        running = True
        finished = False
        message = 'Arrow keys: move / hit wall twice'
        while running:
            now = p.get_time()
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
                    if finished or transitioned:
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
                        if completed == total:
                            finished = True
                            message = 'Maze complete! Battle is not implemented yet.'
                        else:
                            maze = Maze(size, maze.exit)
                            player.position = maze.entrance
                        # Keep processing releases, but do not move in the new maze yet.
                        transitioned = True
            p.clear_canvas()
            maze.draw(maze_sheet, font)
            player.draw(character_sheet, maze, now)
            font.draw(100, 550, f'BulBreak | {size}x{size} | {min(completed + 1, total)}/{total}', (20, 20, 20))
            font.draw(100, 70, message, (20, 20, 20))
            font.draw(100, 45, 'IN: entrance / OUT: exit | Close window to quit', (20, 20, 20))
            p.update_canvas()
            p.delay(0.01)
    finally:
        p.close_canvas()


if __name__ == '__main__':
    main()
