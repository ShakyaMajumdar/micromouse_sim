from typing import Callable, TypeAlias

from ..direction_flags import DirectionFlags
from .dfs_generator import dfs_generator
from .eller_generator import eller_generator

MazeGenerator: TypeAlias = Callable[[int, int, tuple[int, int], tuple[int, int]], list[list[DirectionFlags]]]

__all__ = ["MazeGenerator", "dfs_generator", "eller_generator"]
