"""Maze rules; coordinates are (row, column), starting at the top left."""
# 이곳은 maze_gamemode에서 작동되며 이곳에서 미로에서 판정해야될 코드를 구현할 것
import random


class maze:
    DISPLAY_SIZE = 400


class Maze:
    DISPLAY_SIZE = 400
    WALL_FRAME_SECONDS = 0.15

    @property
    def cell_size(self):
        return self.DISPLAY_SIZE / self.size

    def __init__(self, size, entrance=(0, 0)):
        if size != 6:
            raise ValueError("미로 크기는 6×6만 사용할 수 있습니다")
        self.size = size
        self.entrance = entrance
        self.walls = {}
        for row in range(size):
            candidates = [col for col in range(size) if (row, col) != entrance]
            for col in random.sample(candidates, size // 2):
                self.walls[row, col] = 2
        passages = [(r, c) for r in range(size) for c in range(size)
                    if (r, c) not in self.walls
                    and not self.in_exit_exclusion((r, c))]
        self.exit = random.choice(passages)

    def in_exit_exclusion(self, position):
        """Exclude a start-centered square; even sides extend down/right."""
        side = self.size // 2 + 1
        before = (side - 1) // 2
        after = side // 2
        return all(-before <= value - origin <= after
                   for value, origin in zip(position, self.entrance))

    def step(self, position, direction):
        target = tuple(a + b for a, b in zip(position, direction))
        if not all(0 <= value < self.size for value in target):
            return position, 'blocked'
        if target in self.walls:
            self.walls[target] -= 1
            if self.walls[target] == 0:
                del self.walls[target]
                return position, 'broken'
            return position, 'hit'
        return target, 'exit' if target == self.exit else 'moved'

    def center(self, position):
        # Screen top-left (100, 100), bottom-right (500, 500).
        cell = self.cell_size
        row, col = position
        return 100 + (col + 0.5) * cell, 500 - (row + 0.5) * cell

    def draw(self, sheet, font, now=0.0):
        from codes.hud import game_text as text
        cell = self.cell_size
        width, height = sheet.w // 4, sheet.h // 2
        for row in range(self.size):
            for col in range(self.size):
                position = row, col
                x, y = self.center(position)
                hp = self.walls.get(position, 0)
                # Top columns 2/3: passage or intact wall / damaged wall.
                # Column 1 is the exit, column 4 is the game-over overlay.
                frame = 2 if hp == 1 else 1
                sheet.clip_draw(frame * width, height, width, height,
                                x, y, cell, cell)
                if hp:
                    frame = int(now / self.WALL_FRAME_SECONDS) % 4
                    sheet.clip_draw(frame * width, 0, width, height,
                                    x, y, cell * .55, cell * .55)
                    text(font, x - 4, y, str(hp))
                if position == self.exit:
                    sheet.clip_draw(0, height, width, height,
                                    x, y, cell, cell)
        for position, label, color in [(self.entrance, 'IN', (0, 150, 70)),
                                        (self.exit, 'OUT', (30, 80, 240))]:
            x, y = self.center(position)
            text(font, x - cell * .45, y + cell * .3, label)
