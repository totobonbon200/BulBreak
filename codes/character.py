"""Player state and the top-row maze animation."""
class Character:
    def __init__(self, position):
        self.position = position
        self.animation_until = 0.0

    def react(self, now):
        self.animation_until = now + 0.15

    def draw(self, sheet, maze, now):
        width, height = sheet.w // 4, sheet.h // 4
        frame = int(now < self.animation_until)
        x, y = maze.center(self.position)
        size = maze.cell_size * .7
        sheet.clip_draw(frame * width, 3 * height, width, height,
                        x, y, size, size)
