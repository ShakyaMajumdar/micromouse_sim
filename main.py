import numpy as np
import imageio

import json
import random
import PIL.Image
import dataclasses
from dataclasses import dataclass
from enum import IntFlag, auto
from typing import Any

MAZE_SIZE = (16, 16)
RENDER_CELL_SIZE = 10
FPS = 30


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

    def add_to(self, pos: tuple[int, int]) -> tuple[int, int]:
        r, c = pos
        dr, dc = self.to_delta()
        return (r + dr, c + dc)


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

    def dumps(self):
        return json.dumps(dataclasses.asdict(self))

    @classmethod
    def load(cls, fp: str):
        with open(fp) as f:
            return cls.loads(f.read())

    @classmethod
    def loads(cls, s: str):
        d = json.loads(s)
        d["grid"] = [[DirectionFlags(n) for n in row] for row in d["grid"]]
        d["src"] = tuple(d["src"])
        d["dst"] = tuple(d["dst"])
        return cls(**d)

    def __hash__(self) -> int:
        return hash(tuple(tuple(r) for r in self.grid))


class Mouse:
    def __init__(self, maze: Maze, writer: Any):
        self.maze = maze
        self.writer = writer
        self.pos = maze.src


class DfsMouse(Mouse):
    def run(self):
        visited = [[False for _ in range(self.maze.n)] for _ in range(self.maze.m)]
        stack = [self.maze.src]
        visited[self.maze.src[0]][self.maze.src[1]] = True
        self.writer.append_data(np.array(render(self.maze, self)))
        while stack:
            self.pos = r, c = stack.pop()
            self.writer.append_data(np.array(render(self.maze, self)))
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

        self.writer.close()


class FloodFillMouse(Mouse):
    def __init__(self, maze: Maze, writer: Any) -> None:
        super().__init__(maze, writer)
        self.dists: list[list[int]] = [
            [
                abs(r - self.maze.dst[0]) + abs(c - self.maze.dst[1])
                for c in range(self.maze.n)
            ]
            for r in range(self.maze.m)
        ]

    def run(self):
        dists = self.dists
        r, c = self.pos
        self.writer.append_data(np.array(render(self.maze, self)))
        while dists[r][c] != 0:
            unwalled_dirs = [d for d in DirectionFlags if not d & self.maze.grid[r][c]]
            min_nbr_dist = min(self.dist_in_dir(d, r, c) for d in unwalled_dirs)
            d = next(
                d for d in unwalled_dirs if self.dist_in_dir(d, r, c) == min_nbr_dist
            )
            self.cascade_changes(r, c)
            self.pos = r, c = d.add_to((r, c))
            self.writer.append_data(np.array(render(self.maze, self)))
        self.writer.close()

    def dist_in_dir(self, d: DirectionFlags, r: int, c: int) -> int:
        if d & self.maze.grid[r][c]:
            assert False
        nr, nc = d.add_to((r, c))
        return self.dists[nr][nc]

    def cascade_changes(self, r: int, c: int):
        unwalled_dirs = [d for d in DirectionFlags if not d & self.maze.grid[r][c]]
        min_nbr_dist = min(self.dist_in_dir(d, r, c) for d in unwalled_dirs)
        if self.dists[r][c] == min_nbr_dist + 1:
            return
        self.dists[r][c] = min_nbr_dist + 1
        for d in unwalled_dirs:
            nr, nc = d.add_to((r, c))
            self.cascade_changes(nr, nc)


def render(maze: Maze, mouse: Mouse | None = None) -> PIL.Image.Image:
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
            if mouse and (r, c) == mouse.pos:
                canvas[top + 1 : bottom, left + 1 : right] = 63
    return PIL.Image.fromarray(canvas, mode="L")  # type: ignore


def main():
    maze = Maze.generate_random(*MAZE_SIZE)
    maze_id = abs(hash(maze))
    render(maze).save(f"mazes/{maze_id}.png")
    with open(f"mazes/{maze_id}.json", "w") as f:
        f.write(maze.dumps())
    writer = imageio.get_writer(f"out/{maze_id}_floodfill.mp4", fps=FPS)  # type: ignore
    mouse = FloodFillMouse(maze, writer)
    mouse.run()


main()
