import pyxel


class App:
    def __init__(self):
        self.BOARD_WIDTH = 10
        self.BOARD_HEIGHT = 20
        self.BLOCK_SIZE = 8

        self.WINDOW_WIDTH = self.BOARD_WIDTH * self.BLOCK_SIZE + 80
        self.WINDOW_HEIGHT = self.BOARD_HEIGHT * self.BLOCK_SIZE

        self.COLORS = [0, 3, 1, 2, 4, 5, 6, 7]
        self.TETROMINOS = [
            {"shape": [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]], "color": 1},
            {"shape": [[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0]], "color": 2},
            {"shape": [[0, 0, 0, 0], [1, 1, 1, 0], [0, 1, 0, 0], [0, 0, 0, 0]], "color": 3},
            {"shape": [[0, 0, 0, 0], [0, 1, 1, 0], [1, 1, 0, 0], [0, 0, 0, 0]], "color": 4},
            {"shape": [[0, 0, 0, 0], [1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0]], "color": 5},
            {"shape": [[0, 0, 0, 0], [1, 0, 0, 0], [1, 1, 1, 0], [0, 0, 0, 0]], "color": 6},
            {"shape": [[0, 0, 0, 0], [0, 0, 1, 0], [1, 1, 1, 0], [0, 0, 0, 0]], "color": 7},
        ]

        pyxel.init(self.WINDOW_WIDTH, self.WINDOW_HEIGHT, title="Pyxel Tetromino")
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.board = [[0 for _ in range(self.BOARD_WIDTH)] for _ in range(self.BOARD_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.piece_x = self.BOARD_WIDTH // 2 - 2
        self.piece_y = 0
        self.score = 0
        self.game_over = False
        self.fall_speed = 30
        self.fall_timer = 0

    def new_piece(self):
        return self.TETROMINOS[pyxel.rndi(0, len(self.TETROMINOS) - 1)].copy()

    def rotate_piece(self, piece):
        new_shape = [[0 for _ in range(4)] for _ in range(4)]
        for y in range(4):
            for x in range(4):
                new_shape[x][3 - y] = piece["shape"][y][x]
        return {"shape": new_shape, "color": piece["color"]}

    def check_collision(self, piece, x_offset, y_offset):
        for y in range(4):
            for x in range(4):
                if piece["shape"][y][x] != 0:
                    board_x = self.piece_x + x + x_offset
                    board_y = self.piece_y + y + y_offset
                    if not (0 <= board_x < self.BOARD_WIDTH and 0 <= board_y < self.BOARD_HEIGHT):
                        return True
                    if self.board[board_y][board_x] != 0:
                        return True
        return False

    def merge_piece(self):
        for y in range(4):
            for x in range(4):
                if self.current_piece["shape"][y][x] != 0:
                    self.board[self.piece_y + y][self.piece_x + x] = self.current_piece["color"]

    def clear_lines(self):
        lines_cleared = 0
        new_board = []
        for r in range(self.BOARD_HEIGHT):
            if 0 not in self.board[r]:
                lines_cleared += 1
            else:
                new_board.append(self.board[r])
        for _ in range(lines_cleared):
            new_board.insert(0, [0 for _ in range(self.BOARD_WIDTH)])
        self.board = new_board
        if lines_cleared > 0:
            if lines_cleared == 1:
                self.score += 100
            elif lines_cleared == 2:
                self.score += 300
            elif lines_cleared == 3:
                self.score += 500
            elif lines_cleared == 4:
                self.score += 800

    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.reset_game()
            return

        self.fall_timer += 1
        if self.fall_timer >= self.fall_speed:
            if not self.check_collision(self.current_piece, 0, 1):
                self.piece_y += 1
            else:
                self.merge_piece()
                self.clear_lines()
                self.current_piece = self.next_piece
                self.next_piece = self.new_piece()
                self.piece_x = self.BOARD_WIDTH // 2 - 2
                self.piece_y = 0
                if self.check_collision(self.current_piece, 0, 0):
                    self.game_over = True
            self.fall_timer = 0

        if pyxel.btnp(pyxel.KEY_LEFT, 0, 5):
            if not self.check_collision(self.current_piece, -1, 0):
                self.piece_x -= 1

        if pyxel.btnp(pyxel.KEY_RIGHT, 0, 5):
            if not self.check_collision(self.current_piece, 1, 0):
                self.piece_x += 1

        if pyxel.btnp(pyxel.KEY_DOWN, 0, 2):
            if not self.check_collision(self.current_piece, 0, 1):
                self.piece_y += 1
            self.fall_timer = 0

        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_X):
            rotated_piece = self.rotate_piece(self.current_piece)
            if not self.check_collision(rotated_piece, 0, 0):
                self.current_piece = rotated_piece

        if pyxel.btnp(pyxel.KEY_SPACE):
            while not self.check_collision(self.current_piece, 0, 1):
                self.piece_y += 1
            self.merge_piece()
            self.clear_lines()
            self.current_piece = self.next_piece
            self.next_piece = self.new_piece()
            self.piece_x = self.BOARD_WIDTH // 2 - 2
            self.piece_y = 0
            if self.check_collision(self.current_piece, 0, 0):
                self.game_over = True

    def draw(self):
        pyxel.cls(0)
        for y in range(self.BOARD_HEIGHT):
            for x in range(self.BOARD_WIDTH):
                color = self.board[y][x]
                if color != 0:
                    pyxel.rect(
                        x * self.BLOCK_SIZE, y * self.BLOCK_SIZE, self.BLOCK_SIZE, self.BLOCK_SIZE, self.COLORS[color]
                    )
                    pyxel.rectb(x * self.BLOCK_SIZE, y * self.BLOCK_SIZE, self.BLOCK_SIZE, self.BLOCK_SIZE, 0)

        for y in range(4):
            for x in range(4):
                if self.current_piece["shape"][y][x] != 0:
                    color = self.current_piece["color"]
                    pyxel.rect(
                        (self.piece_x + x) * self.BLOCK_SIZE,
                        (self.piece_y + y) * self.BLOCK_SIZE,
                        self.BLOCK_SIZE,
                        self.BLOCK_SIZE,
                        self.COLORS[color],
                    )
                    pyxel.rectb(
                        (self.piece_x + x) * self.BLOCK_SIZE,
                        (self.piece_y + y) * self.BLOCK_SIZE,
                        self.BLOCK_SIZE,
                        self.BLOCK_SIZE,
                        0,
                    )

        pyxel.text(self.BOARD_WIDTH * self.BLOCK_SIZE + 10, 10, "NEXT:", 7)

        for y in range(4):
            for x in range(4):
                if self.next_piece["shape"][y][x] != 0:
                    color = self.next_piece["color"]
                    pyxel.rect(
                        self.BOARD_WIDTH * self.BLOCK_SIZE + 10 + x * self.BLOCK_SIZE,
                        30 + y * self.BLOCK_SIZE,
                        self.BLOCK_SIZE,
                        self.BLOCK_SIZE,
                        self.COLORS[color],
                    )
                    pyxel.rectb(
                        self.BOARD_WIDTH * self.BLOCK_SIZE + 10 + x * self.BLOCK_SIZE,
                        30 + y * self.BLOCK_SIZE,
                        self.BLOCK_SIZE,
                        self.BLOCK_SIZE,
                        0,
                    )

        pyxel.text(self.BOARD_WIDTH * self.BLOCK_SIZE + 10, 80, f"SCORE: {self.score}", 7)

        if self.game_over:
            pyxel.rect(0, self.WINDOW_HEIGHT // 2 - 20, self.WINDOW_WIDTH, 40, 0)
            pyxel.text(self.WINDOW_WIDTH // 2 - 30, self.WINDOW_HEIGHT // 2 - 10, "GAME OVER", 7)
            pyxel.text(self.WINDOW_WIDTH // 2 - 65, self.WINDOW_HEIGHT // 2 + 5, "Press 'Enter' to Restart", 7)


App()
