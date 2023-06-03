from typing import Iterable
from ..maze import Maze


class Mouse:
    def __init__(self, maze: Maze):
        self.maze = maze
        self.pos = maze.src

    def run(self) -> Iterable[tuple[int, int]]:
        raise NotImplementedError
