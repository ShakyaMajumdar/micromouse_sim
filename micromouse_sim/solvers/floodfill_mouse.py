from ..direction_flags import DirectionFlags
from ..maze import Maze
from .mouse import Mouse


class FloodFillMouse(Mouse):
    def __init__(self, maze: Maze) -> None:
        super().__init__(maze)
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
        yield r, c
        while dists[r][c] != 0:
            unwalled_dirs = [d for d in DirectionFlags if not d & self.maze.grid[r][c]]
            min_nbr_dist = min(self.dist_in_dir(d, r, c) for d in unwalled_dirs)
            d = next(
                d for d in unwalled_dirs if self.dist_in_dir(d, r, c) == min_nbr_dist
            )
            self.cascade_changes(r, c)
            self.pos = r, c = d.add_to((r, c))
            yield r, c

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
