import pyxel


class App:
    """A simple Snake game implementation using Pyxel."""

    def __init__(self):
        """Initializes the Snake game."""
        self.SCREEN_WIDTH = 128
        self.SCREEN_HEIGHT = 128
        self.GRID_SIZE = 8
        self.SNAKE_INITIAL_LENGTH = 3
        self.UPDATE_SPEED = 8
        self.GAME_OVER_TEXT = "GAME OVER"
        self.RESTART_TEXT = "PRESS 'ENTER' TO RESTART"

        pyxel.init(self.SCREEN_WIDTH, self.SCREEN_HEIGHT, title="SNAKE GAME")
        pyxel.fullscreen = False

        self.reset_game()
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        """Resets the game state to its initial conditions."""
        self.snake = []
        start_x = (self.SCREEN_WIDTH // self.GRID_SIZE // 2) * self.GRID_SIZE
        start_y = (self.SCREEN_HEIGHT // self.GRID_SIZE // 2) * self.GRID_SIZE
        for i in range(self.SNAKE_INITIAL_LENGTH):
            self.snake.append([start_x - i * self.GRID_SIZE, start_y])

        self.direction = (self.GRID_SIZE, 0)
        self.food = self._generate_food_position()
        self.score = 0
        self.game_over = False
        self.next_direction = self.direction

    def _generate_food_position(self):
        """Generates a random position for the food, ensuring it's not on the snake."""
        while True:
            fx = pyxel.rndi(0, (self.SCREEN_WIDTH // self.GRID_SIZE) - 1) * self.GRID_SIZE
            fy = pyxel.rndi(0, (self.SCREEN_HEIGHT // self.GRID_SIZE) - 1) * self.GRID_SIZE
            food_pos = [fx, fy]
            if food_pos not in self.snake:
                return food_pos

    def update(self):
        """Updates the game state based on user input and game logic."""
        if pyxel.btnp(pyxel.KEY_RETURN) and self.game_over:
            self.reset_game()
            return

        if self.game_over:
            return
        if pyxel.btnp(pyxel.KEY_UP) and self.direction[1] == 0:
            self.next_direction = (0, -self.GRID_SIZE)
        elif pyxel.btnp(pyxel.KEY_DOWN) and self.direction[1] == 0:
            self.next_direction = (0, self.GRID_SIZE)
        elif pyxel.btnp(pyxel.KEY_LEFT) and self.direction[0] == 0:
            self.next_direction = (-self.GRID_SIZE, 0)
        elif pyxel.btnp(pyxel.KEY_RIGHT) and self.direction[0] == 0:
            self.next_direction = (self.GRID_SIZE, 0)

        if pyxel.frame_count % self.UPDATE_SPEED == 0:
            self.direction = self.next_direction
            head_x, head_y = self.snake[0]
            new_head = [head_x + self.direction[0], head_y + self.direction[1]]

            if not (0 <= new_head[0] < self.SCREEN_WIDTH and 0 <= new_head[1] < self.SCREEN_HEIGHT):
                self.game_over = True
                return
            if new_head in self.snake:
                self.game_over = True
                return

            self.snake.insert(0, new_head)

            if new_head == self.food:
                self.score += 1
                self.food = self._generate_food_position()
            else:
                self.snake.pop()

    def draw(self):
        """Draws all game elements on the screen."""
        pyxel.cls(0)
        for x, y in self.snake:
            pyxel.rect(x, y, self.GRID_SIZE, self.GRID_SIZE, 3)

        pyxel.rect(self.food[0], self.food[1], self.GRID_SIZE, self.GRID_SIZE, 8)

        pyxel.text(5, 5, f"SCORE: {self.score}", 7)

        if self.game_over:
            pyxel.text(
                (self.SCREEN_WIDTH - (len(self.GAME_OVER_TEXT) * 4)) // 2,
                self.SCREEN_HEIGHT // 2 - 10,
                self.GAME_OVER_TEXT,
                8,
            )
            pyxel.text(
                (self.SCREEN_WIDTH - (len(self.RESTART_TEXT) * 4)) // 2,
                self.SCREEN_HEIGHT // 2,
                self.RESTART_TEXT,
                7,
            )


App()
