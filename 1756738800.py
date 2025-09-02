import math

import pyxel

SCREEN_WIDTH = 256
SCREEN_HEIGHT = 192
PADDLE_WIDTH = 40
PADDLE_HEIGHT = 8
PADDLE_Y = SCREEN_HEIGHT - PADDLE_HEIGHT - 5
BALL_RADIUS = 3
BLOCK_WIDTH = 20
BLOCK_HEIGHT = 10
BLOCK_ROWS = 5
BLOCK_COLS = 12
INITIAL_BALL_SPEED_MAGNITUDE = 2.5
PADDLE_SPEED = 3


class App:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Pyxel Breakout")
        pyxel.sounds[0].set("a3a2c2", "p", "7", "n", 5)
        pyxel.sounds[1].set("c3f3", "p", "7", "n", 5)
        pyxel.sounds[2].set("f1e1d1", "n", "7", "n", 5)
        pyxel.sounds[3].set("g4c4", "p", "7", "n", 5)
        self.game_state = "TITLE"
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.paddle_x = (SCREEN_WIDTH - PADDLE_WIDTH) / 2
        self.ball_x = SCREEN_WIDTH / 2
        self.ball_y = PADDLE_Y - BALL_RADIUS - 1
        self.ball_vx = INITIAL_BALL_SPEED_MAGNITUDE * (1 if pyxel.rndi(0, 1) else -1) * 0.7
        self.ball_vy = -INITIAL_BALL_SPEED_MAGNITUDE * 0.7
        self.score = 0
        self.lives = 3
        self.blocks = []

        total_blocks_width = BLOCK_COLS * BLOCK_WIDTH
        start_x_offset = (SCREEN_WIDTH - total_blocks_width) / 2
        if start_x_offset < 0:
            start_x_offset = 0
        for r in range(BLOCK_ROWS):
            for c in range(BLOCK_COLS):
                block_x = start_x_offset + c * BLOCK_WIDTH
                block_y = r * BLOCK_HEIGHT + 20
                self.blocks.append({"x": block_x, "y": block_y, "alive": True, "color": (r % 6) + 8})

    def update(self):
        if self.game_state == "TITLE":
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.game_state = "PLAYING"
                self.reset_game()
            return
        if self.game_state == "GAME_OVER" or self.game_state == "GAME_CLEAR":
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.game_state = "TITLE"
            return

        if pyxel.btn(pyxel.KEY_LEFT):
            self.paddle_x = max(0, self.paddle_x - PADDLE_SPEED)
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.paddle_x = min(SCREEN_WIDTH - PADDLE_WIDTH, self.paddle_x + PADDLE_SPEED)

        self.ball_x += self.ball_vx
        self.ball_y += self.ball_vy
        if self.ball_x - BALL_RADIUS < 0:
            self.ball_x = BALL_RADIUS
            self.ball_vx *= -1
            pyxel.play(3, 0)
        elif self.ball_x + BALL_RADIUS > SCREEN_WIDTH:
            self.ball_x = SCREEN_WIDTH - BALL_RADIUS
            self.ball_vx *= -1
            pyxel.play(3, 0)
        if self.ball_y - BALL_RADIUS < 0:
            self.ball_y = BALL_RADIUS
            self.ball_vy *= -1
            pyxel.play(3, 0)

        if (
            self.ball_vy > 0
            and PADDLE_Y <= self.ball_y + BALL_RADIUS <= PADDLE_Y + PADDLE_HEIGHT
            and self.paddle_x <= self.ball_x <= self.paddle_x + PADDLE_WIDTH
        ):
            self.ball_vy *= -1
            relative_impact = (self.ball_x - (self.paddle_x + PADDLE_WIDTH / 2)) / (PADDLE_WIDTH / 2)
            self.ball_vx = relative_impact * INITIAL_BALL_SPEED_MAGNITUDE * 1.5
            max_vx = INITIAL_BALL_SPEED_MAGNITUDE * 2
            if abs(self.ball_vx) > max_vx:
                self.ball_vx = max_vx * (1 if self.ball_vx > 0 else -1)
            target_speed = INITIAL_BALL_SPEED_MAGNITUDE + (self.score / 2000)
            if target_speed > INITIAL_BALL_SPEED_MAGNITUDE * 2:
                target_speed = INITIAL_BALL_SPEED_MAGNITUDE * 2
            vy_squared = target_speed**2 - self.ball_vx**2
            if vy_squared < 0:
                vy_squared = 0
            self.ball_vy = -math.sqrt(vy_squared)
            pyxel.play(3, 1)

        if self.ball_y + BALL_RADIUS > SCREEN_HEIGHT:
            self.lives -= 1
            pyxel.play(3, 2)
            if self.lives <= 0:
                self.game_state = "GAME_OVER"
            else:
                self.ball_x = self.paddle_x + PADDLE_WIDTH / 2
                self.ball_y = PADDLE_Y - BALL_RADIUS - 1
                self.ball_vx = INITIAL_BALL_SPEED_MAGNITUDE * (1 if pyxel.rndi(0, 1) else -1) * 0.7
                self.ball_vy = -INITIAL_BALL_SPEED_MAGNITUDE * 0.7

        blocks_remaining = 0
        for block in self.blocks:
            if block["alive"]:
                blocks_remaining += 1
                block_x, block_y = block["x"], block["y"]
                if (
                    block_x < self.ball_x + BALL_RADIUS
                    and self.ball_x - BALL_RADIUS < block_x + BLOCK_WIDTH
                    and block_y < self.ball_y + BALL_RADIUS
                    and self.ball_y - BALL_RADIUS < block_y + BLOCK_HEIGHT
                ):
                    block["alive"] = False
                    self.score += 100
                    pyxel.play(3, 3)
                    self.ball_vy *= -1
                    current_speed_mag = math.sqrt(self.ball_vx**2 + self.ball_vy**2)
                    if current_speed_mag < INITIAL_BALL_SPEED_MAGNITUDE * 2:
                        speed_boost_factor = 1.02
                        self.ball_vx *= speed_boost_factor
                        self.ball_vy *= speed_boost_factor
                    break

        if blocks_remaining == 0:
            self.game_state = "GAME_CLEAR"

    def draw(self):
        pyxel.cls(0)
        if self.game_state == "TITLE":
            text_breakout = "BREAKOUT"
            x_breakout = (SCREEN_WIDTH - len(text_breakout) * 4) / 2
            pyxel.text(x_breakout, SCREEN_HEIGHT / 2 - 20, text_breakout, 7)

            text_start = "Press ENTER to Start"
            x_start = (SCREEN_WIDTH - len(text_start) * 4) / 2
            pyxel.text(x_start, SCREEN_HEIGHT / 2 + 10, text_start, 7)
            return

        pyxel.rect(self.paddle_x, PADDLE_Y, PADDLE_WIDTH, PADDLE_HEIGHT, 11)
        pyxel.circ(self.ball_x, self.ball_y, BALL_RADIUS, 7)

        for block in self.blocks:
            if block["alive"]:
                pyxel.rect(block["x"], block["y"], BLOCK_WIDTH, BLOCK_HEIGHT, block["color"])

        pyxel.text(0, 0, f"SCORE: {self.score}", 7)
        pyxel.text(0, 10, f"LIVES: {self.lives}", 7)

        if self.game_state == "GAME_OVER":
            text_game_over = "GAME OVER"
            x_game_over = (SCREEN_WIDTH - len(text_game_over) * 4) / 2
            pyxel.text(x_game_over, SCREEN_HEIGHT / 2 - 10, text_game_over, 8)

            text_press_enter = "Press ENTER"
            x_press_enter = (SCREEN_WIDTH - len(text_press_enter) * 4) / 2
            pyxel.text(x_press_enter, SCREEN_HEIGHT / 2 + 10, text_press_enter, 7)
        elif self.game_state == "GAME_CLEAR":
            text_game_clear = "GAME CLEAR!"
            x_game_clear = (SCREEN_WIDTH - len(text_game_clear) * 4) / 2
            pyxel.text(x_game_clear, SCREEN_HEIGHT / 2 - 10, text_game_clear, 10)

            text_press_enter = "Press ENTER"
            x_press_enter = (SCREEN_WIDTH - len(text_press_enter) * 4) / 2
            pyxel.text(x_press_enter, SCREEN_HEIGHT / 2 + 10, text_press_enter, 7)


App()
