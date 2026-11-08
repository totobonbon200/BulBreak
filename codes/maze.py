"""Maze rules; coordinates are (row, column), starting at the top left."""
import random


class Maze:
    DISPLAY_SIZE = 400

    @property
    def cell_size(self):
        return self.DISPLAY_SIZE / self.size

    def __init__(self, size, entrance=(0, 0)):
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

    def draw(self, sheet, font):
        from pico2d import draw_rectangle
        cell = self.cell_size
        width, height = sheet.w // 4, sheet.h // 2
        for row in range(self.size):
            for col in range(self.size):
                position = row, col
                x, y = self.center(position)
                hp = self.walls.get(position, 0)
                frame = 1 if hp == 2 else 2 if hp == 1 else 0
                sheet.clip_draw(frame * width, height, width, height,
                                x, y, cell, cell)
                if hp:
                    # Temporary mapping: bottom columns 1/2 mean 1/2 hits left.
                    sheet.clip_draw((hp - 1) * width, 0, width, height,
                                    x, y, cell * .55, cell * .55)
                    font.draw(x - 4, y, str(hp), (220, 40, 40))
                draw_rectangle(x - cell / 2, y - cell / 2,
                               x + cell / 2, y + cell / 2)
        for position, label, color in [(self.entrance, 'IN', (0, 150, 70)),
                                        (self.exit, 'OUT', (30, 80, 240))]:
            x, y = self.center(position)
            font.draw(x - cell * .45, y + cell * .3, label, color)
