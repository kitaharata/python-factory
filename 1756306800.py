import pyxel

BOARD_SIZE = 8
TILE_SIZE = 30
BOARD_OFFSET_X = 10
BOARD_OFFSET_Y = 10
WIDTH = BOARD_SIZE * TILE_SIZE + BOARD_OFFSET_X * 2
HEIGHT = BOARD_SIZE * TILE_SIZE + BOARD_OFFSET_Y * 2 + 50

EMPTY = 0
BLACK = 1
WHITE = 2

COLOR_BOARD_DARK = 3
COLOR_BOARD_LIGHT = 2
COLOR_BLACK_PIECE = 0
COLOR_WHITE_PIECE = 7
COLOR_HIGHLIGHT = 10
COLOR_TEXT = 7

RESTART_BUTTON_X = BOARD_OFFSET_X + 115
RESTART_BUTTON_Y = HEIGHT - 22
RESTART_BUTTON_W = 40
RESTART_BUTTON_H = 10
COLOR_BUTTON_BG = 5
COLOR_BUTTON_TEXT = 0


class App:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Reversi")
        pyxel.mouse(True)

        self.ai_player = WHITE
        self.ai_move_delay = 30
        self.ai_timer = 0

        self.reset_game()
        self.message = ""

        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.board[3][3] = WHITE
        self.board[3][4] = BLACK
        self.board[4][3] = BLACK
        self.board[4][4] = WHITE

        self.turn = BLACK
        self.game_over = False
        self.winner = None
        self.valid_moves = self._get_valid_moves(self.turn)
        self.message = ""
        self.ai_timer = 0

    def _is_on_board(self, r, c):
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

    def _is_valid_move_direction(self, r, c, dr, dc, player):
        opponent = BLACK if player == WHITE else WHITE
        r_curr, c_curr = r + dr, c + dc
        count_flipped = 0
        while self._is_on_board(r_curr, c_curr) and self.board[r_curr][c_curr] == opponent:
            r_curr += dr
            c_curr += dc
            count_flipped += 1
        if count_flipped > 0 and self._is_on_board(r_curr, c_curr) and self.board[r_curr][c_curr] == player:
            return True
        return False

    def _count_flips_for_direction(self, r, c, dr, dc, player):
        opponent = BLACK if player == WHITE else WHITE
        r_curr, c_curr = r + dr, c + dc
        path = []
        while self._is_on_board(r_curr, c_curr) and self.board[r_curr][c_curr] == opponent:
            path.append((r_curr, c_curr))
            r_curr += dr
            c_curr += dc
        if self._is_on_board(r_curr, c_curr) and self.board[r_curr][c_curr] == player:
            return len(path)
        return 0

    def _count_flips_for_move(self, r, c, player):
        total_flips = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                total_flips += self._count_flips_for_direction(r, c, dr, dc, player)
        return total_flips

    def _is_valid_move(self, r, c, player):
        if not self._is_on_board(r, c) or self.board[r][c] != EMPTY:
            return False
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                if self._is_valid_move_direction(r, c, dr, dc, player):
                    return True
        return False

    def _get_valid_moves(self, player):
        moves = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self._is_valid_move(r, c, player):
                    moves.append((r, c))
        return moves

    def _get_best_ai_move(self, player):
        max_flips = -1
        candidate_moves = []

        for r, c in self.valid_moves:
            flips = self._count_flips_for_move(r, c, player)
            if flips > max_flips:
                max_flips = flips
                candidate_moves = [(r, c)]
            elif flips == max_flips:
                candidate_moves.append((r, c))

        if candidate_moves:
            return candidate_moves[pyxel.rndi(0, len(candidate_moves) - 1)]
        return None

    def _flip_pieces_direction(self, r, c, dr, dc, player):
        opponent = BLACK if player == WHITE else WHITE
        path = []
        r_curr, c_curr = r + dr, c + dc
        while self._is_on_board(r_curr, c_curr) and self.board[r_curr][c_curr] == opponent:
            path.append((r_curr, c_curr))
            r_curr += dr
            c_curr += dc
        if self._is_on_board(r_curr, c_curr) and self.board[r_curr][c_curr] == player:
            for fr, fc in path:
                self.board[fr][fc] = player

    def _make_move(self, r, c, player):
        self.board[r][c] = player
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                if self._is_valid_move_direction(r, c, dr, dc, player):
                    self._flip_pieces_direction(r, c, dr, dc, player)

    def _count_pieces(self):
        black_count = 0
        white_count = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == BLACK:
                    black_count += 1
                elif self.board[r][c] == WHITE:
                    white_count += 1
        return black_count, white_count

    def _advance_turn(self):
        player_just_moved = self.turn
        opponent_player = BLACK if player_just_moved == WHITE else WHITE
        opponent_valid_moves = self._get_valid_moves(opponent_player)

        if opponent_valid_moves:
            self.turn = opponent_player
            self.valid_moves = opponent_valid_moves
            self.message = ""
        else:
            self.message = f"{'BLACK' if opponent_player == BLACK else 'WHITE'} skips turn!"
            current_player_valid_moves = self._get_valid_moves(player_just_moved)
            if current_player_valid_moves:
                self.turn = player_just_moved
                self.valid_moves = current_player_valid_moves
            else:
                self.game_over = True
                black_score, white_score = self._count_pieces()
                if black_score > white_score:
                    self.winner = BLACK
                elif white_score > black_score:
                    self.winner = WHITE
                else:
                    self.winner = EMPTY
        self.ai_timer = 0

    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                mouse_x, mouse_y = pyxel.mouse_x, pyxel.mouse_y
                if (
                    RESTART_BUTTON_X <= mouse_x < RESTART_BUTTON_X + RESTART_BUTTON_W
                    and RESTART_BUTTON_Y <= mouse_y < RESTART_BUTTON_Y + RESTART_BUTTON_H
                ):
                    self.reset_game()
            return
        if self.turn == self.ai_player:
            self.ai_timer += 1
            if self.ai_timer >= self.ai_move_delay:
                if self.valid_moves:
                    r, c = self._get_best_ai_move(self.turn)
                    self._make_move(r, c, self.turn)
                self._advance_turn()
            return
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mouse_x, mouse_y = pyxel.mouse_x, pyxel.mouse_y
            col = (mouse_x - BOARD_OFFSET_X) // TILE_SIZE
            row = (mouse_y - BOARD_OFFSET_Y) // TILE_SIZE
            if self._is_on_board(row, col) and (row, col) in self.valid_moves:
                self._make_move(row, col, self.turn)
                self._advance_turn()

    def draw(self):
        pyxel.cls(0)

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x = c * TILE_SIZE + BOARD_OFFSET_X
                y = r * TILE_SIZE + BOARD_OFFSET_Y
                if (r + c) % 2 == 0:
                    pyxel.rect(x, y, TILE_SIZE, TILE_SIZE, COLOR_BOARD_DARK)
                else:
                    pyxel.rect(x, y, TILE_SIZE, TILE_SIZE, COLOR_BOARD_LIGHT)
                pyxel.rectb(x, y, TILE_SIZE, TILE_SIZE, 1)

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x_center = c * TILE_SIZE + TILE_SIZE // 2 + BOARD_OFFSET_X
                y_center = r * TILE_SIZE + TILE_SIZE // 2 + BOARD_OFFSET_Y
                if self.board[r][c] == BLACK:
                    pyxel.circ(x_center, y_center, TILE_SIZE // 2 - 2, COLOR_BLACK_PIECE)
                elif self.board[r][c] == WHITE:
                    pyxel.circ(x_center, y_center, TILE_SIZE // 2 - 2, COLOR_WHITE_PIECE)

        if not self.game_over:
            for r, c in self.valid_moves:
                x_center = c * TILE_SIZE + TILE_SIZE // 2 + BOARD_OFFSET_X
                y_center = r * TILE_SIZE + TILE_SIZE // 2 + BOARD_OFFSET_Y
                pyxel.circb(x_center, y_center, TILE_SIZE // 2 - 4, COLOR_HIGHLIGHT)

        black_score, white_score = self._count_pieces()
        score_text = f"BLACK: {black_score}  WHITE: {white_score}"
        pyxel.text(BOARD_OFFSET_X, HEIGHT - 40, score_text, COLOR_TEXT)

        if self.message:
            pyxel.text(BOARD_OFFSET_X + 120, HEIGHT - 40, self.message, COLOR_HIGHLIGHT)

        if self.game_over:
            game_over_text = "GAME OVER! "
            if self.winner == BLACK:
                game_over_text += "Black Wins!"
            elif self.winner == WHITE:
                game_over_text += "White Wins!"
            else:
                game_over_text += "Draw!"
            pyxel.text(BOARD_OFFSET_X, HEIGHT - 20, game_over_text, COLOR_HIGHLIGHT)

            pyxel.rect(RESTART_BUTTON_X, RESTART_BUTTON_Y, RESTART_BUTTON_W, RESTART_BUTTON_H, COLOR_BUTTON_BG)
            pyxel.text(RESTART_BUTTON_X + 6, RESTART_BUTTON_Y + 2, "Restart", COLOR_BUTTON_TEXT)
        else:
            turn_text = "Turn: " + ("BLACK" if self.turn == BLACK else "WHITE")
            pyxel.text(BOARD_OFFSET_X, HEIGHT - 20, turn_text, COLOR_TEXT)


App()
