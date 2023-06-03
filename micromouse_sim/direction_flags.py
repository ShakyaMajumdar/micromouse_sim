from enum import IntFlag, auto


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
