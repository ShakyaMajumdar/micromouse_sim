from ..maze import Maze


class Mouse:
    def __init__(self, maze: Maze):
        self.maze = maze
        self.pos = maze.src
