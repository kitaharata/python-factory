import pyxel

WIDTH = 160
HEIGHT = 120
CELL_SIZE = 4
GRID_W = WIDTH // CELL_SIZE
GRID_H = HEIGHT // CELL_SIZE


class GameOfLife:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Game of Life")
        self.grid = self._init_grid()
        pyxel.run(self.update, self.draw)

    def _init_grid(self):
        grid = []
        for _ in range(GRID_H):
            row = [pyxel.rndi(0, 1) for _ in range(GRID_W)]
            grid.append(row)
        return grid

    def update(self):
        if pyxel.btnp(pyxel.KEY_RETURN):
            self.grid = self._init_grid()
        next_grid = [[0 for _ in range(GRID_W)] for _ in range(GRID_H)]
        for y in range(GRID_H):
            for x in range(GRID_W):
                live_neighbors = self._count_live_neighbors(x, y)
                current_cell_state = self.grid[y][x]
                if current_cell_state == 1:
                    if live_neighbors < 2 or live_neighbors > 3:
                        next_grid[y][x] = 0
                    else:
                        next_grid[y][x] = 1
                else:
                    if live_neighbors == 3:
                        next_grid[y][x] = 1
                    else:
                        next_grid[y][x] = 0
        self.grid = next_grid

    def _count_live_neighbors(self, x, y):
        live_neighbors = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
                    live_neighbors += self.grid[ny][nx]
        return live_neighbors

    def draw(self):
        pyxel.cls(0)
        for y in range(GRID_H):
            for x in range(GRID_W):
                if self.grid[y][x] == 1:
                    pyxel.rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, 3)


GameOfLife()
