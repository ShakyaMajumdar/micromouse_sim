import numpy as np
import imageio

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


class DfsMouse:
    def __init__(self, maze: Maze) -> None:
        self.maze = maze
        self.pos = maze.src

    def run(self):
        visited = [[False for _ in range(self.maze.n)] for _ in range(self.maze.m)]
        stack = [self.maze.src]
        visited[self.maze.src[0]][self.maze.src[1]] = True

        writer = imageio.get_writer("out/video.mp4", fps=30)  # type: ignore
        while stack:
            self.pos = r, c = stack.pop()
            writer.append_data(np.array(render(self.maze, self)))
            if (r, c) == self.maze.dst:
                break
            for direction in DirectionFlags:
                if self.maze.grid[r][c] & direction:
                    continue
                dr, dc = direction.to_delta()
                nr, nc = r + dr, c + dc
                if (
                    not (0 <= nr < self.maze.m and 0 <= nc < self.maze.n)
                    or visited[nr][nc]
                ):
                    continue
                visited[nr][nc] = True
                stack.append((r, c))
                stack.append((nr, nc))

        writer.close()


def render(maze: Maze, mouse: DfsMouse) -> PIL.Image.Image:
    canvas = np.full(
        (RENDER_CELL_SIZE * maze.m + 2, RENDER_CELL_SIZE * maze.n + 2),
        255,
        dtype=np.uint8,
    )
    canvas[0, :] = 0
    canvas[-1, :] = 0
    canvas[:, 0] = 0
    canvas[:, -1] = 0
    for r, row in enumerate(maze.grid):
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
            if (r, c) == maze.dst:
                canvas[top + 1 : bottom, left + 1 : right] = 127
            if (r, c) == mouse.pos:
                canvas[top + 1 : bottom, left + 1 : right] = 63
    return PIL.Image.fromarray(canvas, mode="L")  # type: ignore


def main():
    maze = Maze.generate_random(20, 20)
    mouse = DfsMouse(maze)
    mouse.run()


main()
