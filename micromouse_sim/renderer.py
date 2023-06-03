from typing import Any
import numpy as np

from .direction_flags import DirectionFlags
from .maze import Maze


class Renderer:
    def __init__(self, maze: Maze, writer: Any, *, render_cell_size: int) -> None:
        self.maze = maze
        self.writer = writer
        self.render_cell_size = render_cell_size
    
    def render(self, mouse_pos: tuple[int, int] | None = None):
        canvas = np.full(
            (self.render_cell_size * self.maze.m + 2, self.render_cell_size * self.maze.n + 2),
            255,
            dtype=np.uint8,
        )
        
        canvas[0, :] = 0
        canvas[-1, :] = 0
        canvas[:, 0] = 0
        canvas[:, -1] = 0
        for r, row in enumerate(self.maze.grid):
            for c, walls in enumerate(row):
                top = 1 + self.render_cell_size * r
                bottom = top + self.render_cell_size - 1
                left = 1 + self.render_cell_size * c
                right = left + self.render_cell_size - 1
                if walls & DirectionFlags.N:
                    canvas[top, left : right + 1] = 0
                if walls & DirectionFlags.S:
                    canvas[bottom, left : right + 1] = 0
                if walls & DirectionFlags.E:
                    canvas[top : bottom + 1, right] = 0
                if walls & DirectionFlags.W:
                    canvas[top : bottom + 1, left] = 0
                if (r, c) == self.maze.dst:
                    canvas[top + 1 : bottom, left + 1 : right] = 127
                if (r, c) == mouse_pos:
                    canvas[top + 1 : bottom, left + 1 : right] = 63
        return canvas

    def add_frame(self, mouse_pos: tuple[int, int]):
        self.writer.append_data(self.render(mouse_pos))

    def __enter__(self):
        return self
    
    def __exit__(self, *_):
        self.writer.close()
