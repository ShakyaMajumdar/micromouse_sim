from ..direction_flags import DirectionFlags
from .mouse import Mouse


class DfsMouse(Mouse):
    def run(self):
        visited = [[False for _ in range(self.maze.n)] for _ in range(self.maze.m)]
        stack = [self.maze.src]
        visited[self.maze.src[0]][self.maze.src[1]] = True
        yield self.maze.src
        while stack:
            self.pos = r, c = stack.pop()
            yield r, c
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
