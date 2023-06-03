import PIL.Image
import imageio

from micromouse_sim import Maze, dfs_generator, Renderer, FloodFillMouse

MAZE_SIZE = (16, 16)
RENDER_CELL_SIZE = 10
FPS = 30


def main():
    maze = Maze.generate_random(dfs_generator, *MAZE_SIZE)
    maze_id = abs(hash(maze))
    with open(f"mazes/{maze_id}.json", "w") as f:
        f.write(maze.dumps())
    writer = imageio.get_writer(f"out/{maze_id}_floodfill.mp4", fps=FPS)  # type: ignore
    mouse = FloodFillMouse(maze)
    with Renderer(maze, writer, render_cell_size=RENDER_CELL_SIZE) as renderer:
        PIL.Image.fromarray(renderer.render()).save(f"mazes/{maze_id}.png")  # type: ignore
        for pos in mouse.run():
            renderer.add_frame(mouse_pos=pos)


main()
