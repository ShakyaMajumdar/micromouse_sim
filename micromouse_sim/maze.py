from dataclasses import dataclass
import dataclasses
import json
import random

from .direction_flags import DirectionFlags
from .generators import MazeGenerator

@dataclass(frozen=True)
class Maze:
    grid: list[list[DirectionFlags]]
    src: tuple[int, int]
    dst: tuple[int, int]
    m: int
    n: int

    @classmethod
    def generate_random(cls, generator: MazeGenerator, m: int, n: int, src: tuple[int, int] | None = None, dst: tuple[int, int] | None = None):
        src = src or (0, 0)
        dst = dst or (random.randrange(m), random.randrange(n))
        grid = generator(m, n, src, dst)
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
