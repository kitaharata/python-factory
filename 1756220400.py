import random

import pyxel

BOARD_SIZE = 4
TILE_SIZE = 40
BOARD_OFFSET_X = 20
BOARD_OFFSET_Y = 20
WINDOW_WIDTH = BOARD_OFFSET_X * 2 + BOARD_SIZE * TILE_SIZE
WINDOW_HEIGHT = BOARD_OFFSET_Y * 2 + BOARD_SIZE * TILE_SIZE + 30

COLOR_BACKGROUND = 1
COLOR_EMPTY_TILE_BG = 6
COLOR_TILE_BORDER = 0
COLOR_TEXT = 0
COLOR_SCORE_TEXT = 6
COLOR_GAME_OVER = 8
COLOR_GAME_WON = 10

TILE_COLORS = {
    0: COLOR_EMPTY_TILE_BG,
    2: 7,
    4: 11,
    8: 10,
    16: 9,
    32: 8,
    64: 12,
    128: 5,
    256: 3,
    512: 13,
    1024: 14,
    2048: 15,
}
MERGE_EFFECT_COLORS = {
    0: 7,  # Black -> White
    1: 12,  # Dark Blue -> Blue
    2: 10,  # Dark Purple -> Yellow (more vibrant)
    3: 11,  # Dark Green -> Light Green
    4: 9,  # Brown -> Orange
    5: 6,  # Dark Grey -> Light Grey
    6: 7,  # Light Grey -> White
    7: 10,  # White -> Yellow (for a glow effect)
    8: 9,  # Red -> Orange
    9: 10,  # Orange -> Yellow
    10: 7,  # Yellow -> White
    11: 7,  # Light Green -> White
    12: 7,  # Blue -> White
    13: 12,  # Indigo -> Blue
    14: 15,  # Pink -> Peach
    15: 7,  # Peach -> White
}


class App:
    def init_board(self):
        """Initializes a new 4x4 game board with all zeros."""
        return [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]

    def get_empty_cells(self):
        """Returns a list of (row, col) tuples for all empty cells."""
        empty_cells = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == 0:
                    empty_cells.append((r, c))
        return empty_cells

    def add_random_tile(self):
        """Adds a new 2 or 4 tile to a random empty spot on the board."""
        empty_cells = self.get_empty_cells()
        if empty_cells:
            r, c = random.choice(empty_cells)
            self.board[r][c] = 2 if random.random() < 0.9 else 4
            return True
        return False

    def compress_row(self, row):
        """Compresses a row by moving all non-zero tiles to one side."""
        new_row = [0] * BOARD_SIZE
        k = 0
        for i in range(BOARD_SIZE):
            if row[i] != 0:
                new_row[k] = row[i]
                k += 1
        return new_row

    def merge_row(self, row, current_score):
        """Merges adjacent identical tiles in a compressed row, updating the score."""
        merged_positions = []
        for i in range(BOARD_SIZE - 1):
            if row[i] != 0 and row[i] == row[i + 1]:
                row[i] *= 2
                current_score += row[i]
                row[i + 1] = 0
                merged_positions.append(i)
        return row, current_score, merged_positions

    def move(self, direction):
        """Applies a move (left, right, up, down) to the board and updates the score."""
        moved = False
        temp_board = [row[:] for row in self.board]
        merge_locations = []
        if direction == "left":
            for r in range(BOARD_SIZE):
                original_row = temp_board[r][:]
                compressed_row = self.compress_row(original_row)
                merged_row, self.score, row_merge_positions = self.merge_row(compressed_row, self.score)
                final_row = self.compress_row(merged_row)
                if original_row != final_row:
                    moved = True
                temp_board[r] = final_row
                for c_idx in row_merge_positions:
                    merge_locations.append((r, c_idx))
        elif direction == "right":
            for r in range(BOARD_SIZE):
                original_row = temp_board[r][:]
                row_rev = original_row[::-1]
                compressed_row_rev = self.compress_row(row_rev)
                merged_row_rev, self.score, row_merge_positions_rev = self.merge_row(compressed_row_rev, self.score)
                final_row = self.compress_row(merged_row_rev)[::-1]
                if original_row != final_row:
                    moved = True
                temp_board[r] = final_row
                for c_idx_rev in row_merge_positions_rev:
                    original_c = BOARD_SIZE - 1 - c_idx_rev
                    merge_locations.append((r, original_c))
        elif direction == "up":
            for c in range(BOARD_SIZE):
                col = [temp_board[r_idx][c] for r_idx in range(BOARD_SIZE)]
                original_col = col[:]
                compressed_col = self.compress_row(original_col)
                merged_col, self.score, col_merge_positions = self.merge_row(compressed_col, self.score)
                final_col = self.compress_row(merged_col)
                if original_col != final_col:
                    moved = True
                for r_idx in range(BOARD_SIZE):
                    temp_board[r_idx][c] = final_col[r_idx]
                for r_idx in col_merge_positions:
                    merge_locations.append((r_idx, c))
        elif direction == "down":
            for c in range(BOARD_SIZE):
                col = [temp_board[r_idx][c] for r_idx in range(BOARD_SIZE)]
                original_col = col[:]
                col_rev = original_col[::-1]
                compressed_col_rev = self.compress_row(col_rev)
                merged_col_rev, self.score, col_merge_positions_rev = self.merge_row(compressed_col_rev, self.score)
                final_col = self.compress_row(merged_col_rev)[::-1]
                if original_col != final_col:
                    moved = True
                for r_idx in range(BOARD_SIZE):
                    temp_board[r_idx][c] = final_col[r_idx]
                for r_idx_rev in col_merge_positions_rev:
                    original_r = BOARD_SIZE - 1 - r_idx_rev
                    merge_locations.append((original_r, c))
        self.board = temp_board
        return moved, merge_locations

    def check_game_over(self):
        """Checks if the game is over (no empty cells and no possible moves)."""
        if self.get_empty_cells():
            return False
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if c < BOARD_SIZE - 1 and self.board[r][c] == self.board[r][c + 1]:
                    return False
                if r < BOARD_SIZE - 1 and self.board[r][c] == self.board[r + 1][c]:
                    return False
        return True

    def check_win(self):
        """Checks if the 2048 tile has been achieved."""
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == 2048:
                    return True
        return False

    def __init__(self):
        pyxel.init(WINDOW_WIDTH, WINDOW_HEIGHT, title="2048 Pyxel")
        self.merge_effect_duration = 10
        self.reset_game()

        pyxel.run(self.update, self.draw)

    def reset_game(self):
        """Resets the game state to start a new game."""
        self.board = self.init_board()
        self.score = 0
        self.game_over = False
        self.game_won = False
        self.merge_effects = {}

        self.add_random_tile()
        self.add_random_tile()

    def update(self):
        """Handles game logic updates, including user input."""
        if self.game_over or self.game_won:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.reset_game()
            return

        effects_to_remove = []
        for pos, timer in self.merge_effects.items():
            self.merge_effects[pos] = timer - 1
            if self.merge_effects[pos] <= 0:
                effects_to_remove.append(pos)
        for pos in effects_to_remove:
            del self.merge_effects[pos]

        moved = False
        current_merge_locations = []
        if pyxel.btnp(pyxel.KEY_LEFT):
            moved, current_merge_locations = self.move("left")
        elif pyxel.btnp(pyxel.KEY_RIGHT):
            moved, current_merge_locations = self.move("right")
        elif pyxel.btnp(pyxel.KEY_UP):
            moved, current_merge_locations = self.move("up")
        elif pyxel.btnp(pyxel.KEY_DOWN):
            moved, current_merge_locations = self.move("down")

        if moved:
            self.add_random_tile()
            for pos in current_merge_locations:
                self.merge_effects[pos] = self.merge_effect_duration
            self.game_won = self.check_win()
            if self.check_game_over():
                self.game_over = True

    def draw(self):
        """Renders the game state to the Pyxel window."""
        pyxel.cls(COLOR_BACKGROUND)
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x = BOARD_OFFSET_X + c * TILE_SIZE
                y = BOARD_OFFSET_Y + r * TILE_SIZE
                tile_value = self.board[r][c]
                tile_color_base = TILE_COLORS.get(tile_value, COLOR_EMPTY_TILE_BG)
                draw_color = tile_color_base
                if (r, c) in self.merge_effects:
                    if (self.merge_effects[(r, c)] // 3) % 2 == 0:
                        effect_color = MERGE_EFFECT_COLORS.get(tile_color_base, COLOR_GAME_WON)
                        draw_color = effect_color
                    else:
                        draw_color = tile_color_base
                pyxel.rect(x, y, TILE_SIZE, TILE_SIZE, draw_color)
                pyxel.rectb(x, y, TILE_SIZE, TILE_SIZE, COLOR_TILE_BORDER)
                if tile_value != 0:
                    text = str(tile_value)
                    text_w = pyxel.FONT_WIDTH * len(text)
                    text_x = x + (TILE_SIZE - text_w) // 2
                    text_y = y + (TILE_SIZE - pyxel.FONT_HEIGHT) // 2
                    pyxel.text(text_x, text_y, text, COLOR_TEXT)

        pyxel.text(BOARD_OFFSET_X, WINDOW_HEIGHT - 20, f"Score: {self.score}", COLOR_SCORE_TEXT)

        if self.game_over:
            msg = "GAME OVER! Press 'Enter' to Restart."
            msg_x = WINDOW_WIDTH // 2 - (len(msg) * pyxel.FONT_WIDTH) // 2
            msg_y = WINDOW_HEIGHT // 2 - pyxel.FONT_HEIGHT // 2
            pyxel.text(msg_x, msg_y, msg, COLOR_GAME_OVER)
        elif self.game_won:
            msg = "YOU WIN! (2048) Press 'Enter' to Restart."
            msg_x = WINDOW_WIDTH // 2 - (len(msg) * pyxel.FONT_WIDTH) // 2
            msg_y = WINDOW_HEIGHT // 2 - pyxel.FONT_HEIGHT // 2
            pyxel.text(msg_x, msg_y, msg, COLOR_GAME_WON)


if __name__ == "__main__":
    App()
