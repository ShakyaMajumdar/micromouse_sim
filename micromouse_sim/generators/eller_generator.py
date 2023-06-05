import itertools
import random
from ..direction_flags import DirectionFlags


def eller_generator(m: int, n: int, src: tuple[int, int], dst: tuple[int, int]):
    grid = [
        [
            DirectionFlags.N | DirectionFlags.S | DirectionFlags.E | DirectionFlags.W
            for _ in range(n)
        ]
        for _ in range(m)
    ]

    counter = itertools.count()
    labels: list[list[int]] = [[next(counter) for _ in range(n)] for _ in range(m)]
    for r, row in enumerate(labels):
        is_last_row = r == m-1
        label_to_col_map: dict[int, set[int]] = {}
        for c, elt in enumerate(row):
            label_to_col_map.setdefault(elt, set()).add(c)
        for c in range(1, n):
            if (is_last_row or random.random() > 0.5) and row[c] != row[c-1]:
                label_to_col_map[row[c]].remove(c)
                row[c] = row[c-1]
                label_to_col_map[row[c]].add(c)
                grid[r][c] &= ~DirectionFlags.W
                grid[r][c-1] &= ~DirectionFlags.E
        if is_last_row:
            break
        for _label, cols in label_to_col_map.items():
            if not cols:
                continue
            to_extend = random.choices(tuple(cols), k=random.randint(1, len(cols)))
            for c in to_extend:
                labels[r+1][c] = labels[r][c]
                grid[r][c] &= ~DirectionFlags.S
                grid[r+1][c] &= ~DirectionFlags.N
    return grid
