import random
from ..direction_flags import DirectionFlags


def dfs_generator(
    m: int,
    n: int,
    src: tuple[int, int],
    dst: tuple[int, int],
):
    grid = [
        [
            DirectionFlags.N | DirectionFlags.S | DirectionFlags.E | DirectionFlags.W
            for _ in range(n)
        ]
        for _ in range(m)
    ]
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
    return grid
