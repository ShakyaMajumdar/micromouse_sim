import numpy as np
import random
import PIL.Image
from dataclasses import dataclass
from enum import IntFlag, auto


RENDER_CELL_SIZE = 10


class DirectionFlags(IntFlag):
    N = auto()
    S = auto()
    E = auto()
    W = auto()

    def to_delta(self) -> tuple[int, int]:
        return {
            DirectionFlags.N: (-1, 0),
            DirectionFlags.S: (1, 0),
            DirectionFlags.E: (0, 1),
            DirectionFlags.W: (0, -1),
        }[self]

    def opposite(self) -> "DirectionFlags":
        return {
            DirectionFlags.N: DirectionFlags.S,
            DirectionFlags.S: DirectionFlags.N,
            DirectionFlags.E: DirectionFlags.W,
            DirectionFlags.W: DirectionFlags.E,
        }[self]


def dfs(
    grid: list[list[DirectionFlags]],
    src: tuple[int, int],
    _dst: tuple[int, int],
    m: int,
    n: int,
):
    visited = [[False for _ in range(n)] for _ in range(m)]
    stack = [src]
    visited[src[0]][src[1]] = True
    while stack:
        r, c = stack.pop()
        directions = list(DirectionFlags)
        random.shuffle(directions)
        for direction in directions:
            dr, dc = direction.to_delta()
            nr, nc = r + dr, c + dc
            # print(nr, nc)
            if not (0 <= nr < m and 0 <= nc < n) or visited[nr][nc]:
                continue
            grid[r][c] &= ~direction  # clear wall in that direction
            grid[nr][nc] &= ~direction.opposite()
            visited[nr][nc] = True
            stack.append((nr, nc))


@dataclass
class Maze:
    grid: list[list[DirectionFlags]]
    src: tuple[int, int]
    dst: tuple[int, int]
    m: int
    n: int

    @classmethod
    def generate_random(cls, m: int, n: int):
        grid = [
            [
                DirectionFlags.N
                | DirectionFlags.S
                | DirectionFlags.E
                | DirectionFlags.W
                for _ in range(n)
            ]
            for _ in range(m)
        ]
        src = (0, 0)
        dst = (random.randrange(m), random.randrange(n))
        dfs(grid, src, dst, m, n)
        return cls(grid, src, dst, m, n)

    def render(self) -> PIL.Image.Image:
        canvas = np.full(
            (RENDER_CELL_SIZE * self.m + 2, RENDER_CELL_SIZE * self.n + 2),
            255,
            dtype=np.uint8,
        )
        canvas[0, :] = 0
        canvas[-1, :] = 0
        canvas[:, 0] = 0
        canvas[:, -1] = 0
        for r, row in enumerate(self.grid):
            for c, walls in enumerate(row):
                top = 1 + RENDER_CELL_SIZE * r
                bottom = top + RENDER_CELL_SIZE - 1
                left = 1 + RENDER_CELL_SIZE * c
                right = left + RENDER_CELL_SIZE - 1
                if walls & DirectionFlags.N:
                    canvas[top, left : right + 1] = 0
                if walls & DirectionFlags.S:
                    canvas[bottom, left : right + 1] = 0
                if walls & DirectionFlags.E:
                    canvas[top : bottom + 1, right] = 0
                if walls & DirectionFlags.W:
                    canvas[top : bottom + 1, left] = 0
                if (r, c) == self.dst:
                    canvas[top+1:bottom, left+1:right] = 127
        return PIL.Image.fromarray(canvas, mode="L")  # type: ignore


Maze.generate_random(50, 50).render().save("./maze.png")
