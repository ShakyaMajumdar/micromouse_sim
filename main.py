import argparse

import PIL.Image
import imageio

from micromouse_sim import (
    Maze,
    dfs_generator,
    Renderer,
    DfsMouse,
    FloodFillMouse,
    MazeGenerator,
    Mouse,
)

generators: dict[str, MazeGenerator] = {"dfs": dfs_generator}

solvers: dict[str, type[Mouse]] = {"dfs": DfsMouse, "floodfill": FloodFillMouse}


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="micromouse_sim",
        description="generate and solve mazes using various algorithms",
    )
    parser.add_argument("rows", type=int, help="number of rows in the maze")
    parser.add_argument("columns", type=int, help="number of columns in the maze")
    parser.add_argument(
        "-g",
        "--generator",
        choices=["dfs"],
        required=True,
        help="algorithm to use for generating the maze",
    )
    parser.add_argument(
        "-s",
        "--solver",
        choices=["dfs", "floodfill"],
        required=True,
        help="algorithm to use for solving the maze",
    )
    parser.add_argument("--fps", type=int, default=30, help="fps of output video")
    parser.add_argument(
        "--cell-size", type=int, default=10, help="size of each cell in output video"
    )
    return parser


def main():
    args = get_parser().parse_args()
    maze = Maze.generate_random(generators[args.generator], args.rows, args.columns)
    maze_id = abs(hash(maze))
    with open(f"mazes/{maze_id}.json", "w") as f:
        f.write(maze.dumps())
    writer = imageio.get_writer(f"out/{maze_id}_{args.solver}.mp4", fps=args.fps)  # type: ignore
    mouse = solvers[args.solver](maze)
    with Renderer(maze, writer, render_cell_size=args.cell_size) as renderer:
        PIL.Image.fromarray(renderer.render()).save(f"mazes/{maze_id}.png")  # type: ignore
        for pos in mouse.run():
            renderer.add_frame(mouse_pos=pos)


main()
