import random

from PIL import Image, ImageDraw

WIDTH = 51
HEIGHT = 51
CELL_SIZE = 10
WALL_COLOR = (0, 0, 0)
PATH_COLOR = (255, 255, 255)
OUTPUT_FILENAME = "maze.png"


def generate_maze(width, height):
    """Generates a maze using the depth-first search (recursive backtracker) algorithm."""
    maze = [[1] * width for _ in range(height)]
    stack = []
    start_x, start_y = (1, 1)
    maze[start_y][start_x] = 0
    stack.append((start_x, start_y))
    while stack:
        current_x, current_y = stack[-1]
        neighbors = []
        if current_y > 1 and maze[current_y - 2][current_x] == 1:
            neighbors.append((current_x, current_y - 2))
        if current_y < height - 2 and maze[current_y + 2][current_x] == 1:
            neighbors.append((current_x, current_y + 2))
        if current_x > 1 and maze[current_y][current_x - 2] == 1:
            neighbors.append((current_x - 2, current_y))
        if current_x < width - 2 and maze[current_y][current_x + 2] == 1:
            neighbors.append((current_x + 2, current_y))
        if neighbors:
            next_x, next_y = random.choice(neighbors)
            wall_x = current_x + (next_x - current_x) // 2
            wall_y = current_y + (next_y - current_y) // 2
            maze[wall_y][wall_x] = 0
            maze[next_y][next_x] = 0
            stack.append((next_x, next_y))
        else:
            stack.pop()

    maze[1][0] = 0
    maze[height - 2][width - 1] = 0
    return maze


def draw_maze(maze_data, cell_size, wall_color, path_color):
    """Creates an image from the generated maze data."""
    maze_height = len(maze_data)
    maze_width = len(maze_data[0])
    img_width = maze_width * cell_size
    img_height = maze_height * cell_size
    image = Image.new("RGB", (img_width, img_height), color=path_color)
    draw = ImageDraw.Draw(image)

    for y in range(maze_height):
        for x in range(maze_width):
            if maze_data[y][x] == 1:
                top_left = (x * cell_size, y * cell_size)
                bottom_right = ((x + 1) * cell_size, (y + 1) * cell_size)
                draw.rectangle([top_left, bottom_right], fill=wall_color)
    return image


if __name__ == "__main__":
    maze = generate_maze(WIDTH, HEIGHT)
    maze_image = draw_maze(maze, CELL_SIZE, WALL_COLOR, PATH_COLOR)
    maze_image = maze_image.convert("1")
    maze_image.save(OUTPUT_FILENAME)
    print(f"Maze generated and saved as '{OUTPUT_FILENAME}'.")
