import random
import tkinter as tk

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_SPEED = 10
ENEMY_WIDTH = 50
ENEMY_HEIGHT = 50
ENEMY_SPEED = 3
BULLET_WIDTH = 5
BULLET_HEIGHT = 15
BULLET_SPEED = 20
UPDATE_DELAY = 30


class Game(tk.Tk):
    """Manages the main game window and game loop."""

    def __init__(self):
        super().__init__()

        self.title("Simple Shooting Game")
        self.canvas = tk.Canvas(self, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="black")
        self.canvas.pack()

        self.player = Player(self.canvas)
        self.enemies = []
        self.bullets = []
        self.score = 0
        self.lives = 3
        self.is_game_over = False

        self.score_text = self.canvas.create_text(
            10, 20, text=f"Score: {self.score}", fill="white", font=("Arial", 16), anchor="w"
        )
        self.lives_text = self.canvas.create_text(
            WINDOW_WIDTH - 10, 20, text=f"Lives: {self.lives}", fill="white", font=("Arial", 16), anchor="e"
        )

        self.bind("<KeyPress-Left>", self.player.start_move_left)
        self.bind("<KeyPress-Right>", self.player.start_move_right)
        self.bind("<KeyRelease-Left>", self.player.stop_move)
        self.bind("<KeyRelease-Right>", self.player.stop_move)
        self.bind("<space>", self.create_bullet)

        self.game_loop()
        self.spawn_enemies()

    def game_loop(self):
        """The main game loop for updating and drawing."""
        if self.is_game_over:
            self.show_game_over()
            return

        self.player.update()
        self.update_bullets()
        self.update_enemies()
        self.check_collisions()

        self.after(UPDATE_DELAY, self.game_loop)

    def spawn_enemies(self):
        """Periodically creates new enemies."""
        if not self.is_game_over:
            self.enemies.extend([Enemy(self.canvas) for _ in range(2)])
            self.after(1500, self.spawn_enemies)

    def create_bullet(self, event):
        """Creates a bullet when the spacebar is pressed."""
        if not self.is_game_over:
            player_pos = self.canvas.bbox(self.player.id)
            if not player_pos:
                return
            bullet = Bullet(self.canvas, player_pos[0] + PLAYER_WIDTH / 2, player_pos[1])
            self.bullets.append(bullet)

    def update_bullets(self):
        """Moves bullets and removes them if they go off-screen."""
        for bullet in self.bullets:
            bullet.update()

        remaining_bullets = []
        for bullet in self.bullets:
            pos = self.canvas.bbox(bullet.id)
            if pos and pos[3] > 0:
                remaining_bullets.append(bullet)
            elif pos:
                self.canvas.delete(bullet.id)
        self.bullets = remaining_bullets

    def update_enemies(self):
        """Moves enemies, handles invasion and player collision."""
        player_pos = self.canvas.bbox(self.player.id)
        if not player_pos:
            return

        enemies_to_remove = set()
        lives_lost = 0

        for enemy in self.enemies:
            enemy.update()
            enemy_pos = self.canvas.bbox(enemy.id)

            if not enemy_pos:
                continue

            if enemy_pos[1] > WINDOW_HEIGHT:
                enemies_to_remove.add(enemy)
                lives_lost += 1
                continue

            if (
                player_pos[0] < enemy_pos[2]
                and player_pos[2] > enemy_pos[0]
                and player_pos[1] < enemy_pos[3]
                and player_pos[3] > enemy_pos[1]
            ):
                enemies_to_remove.add(enemy)
                lives_lost += 1

        if lives_lost > 0:
            self.lives -= lives_lost
            self.update_lives()

        if enemies_to_remove:
            self.enemies = [e for e in self.enemies if e not in enemies_to_remove]
            for enemy in enemies_to_remove:
                self.canvas.delete(enemy.id)

        if self.lives <= 0 and not self.is_game_over:
            self.is_game_over = True

    def check_collisions(self):
        """Checks for collisions between bullets and enemies."""
        bullets_hit = set()
        enemies_hit = set()

        for bullet in self.bullets:
            bullet_pos = self.canvas.bbox(bullet.id)
            if not bullet_pos:
                continue

            for enemy in self.enemies:
                if enemy in enemies_hit:
                    continue

                enemy_pos = self.canvas.bbox(enemy.id)
                if not enemy_pos:
                    continue

                if (
                    bullet_pos[0] < enemy_pos[2]
                    and bullet_pos[2] > enemy_pos[0]
                    and bullet_pos[1] < enemy_pos[3]
                    and bullet_pos[3] > enemy_pos[1]
                ):
                    bullets_hit.add(bullet)
                    enemies_hit.add(enemy)
                    self.score += 10
                    break

        if bullets_hit or enemies_hit:
            self.bullets = [b for b in self.bullets if b not in bullets_hit]
            self.enemies = [e for e in self.enemies if e not in enemies_hit]

            for item in bullets_hit.union(enemies_hit):
                self.canvas.delete(item.id)

            self.update_score()

    def update_score(self):
        """Updates the score display."""
        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")

    def update_lives(self):
        """Updates the lives display."""
        if self.lives < 0:
            self.lives = 0
        self.canvas.itemconfig(self.lives_text, text=f"Lives: {self.lives}")

    def show_game_over(self):
        """Displays the Game Over message."""
        self.canvas.create_text(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2, text="GAME OVER", fill="white", font=("Arial", 40))
        self.canvas.create_text(
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2 + 50,
            text=f"Final Score: {self.score}",
            fill="white",
            font=("Arial", 20),
        )


class Player:
    """Represents the player's ship."""

    def __init__(self, canvas):
        self.canvas = canvas
        self.id = self.canvas.create_polygon(
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT - PLAYER_HEIGHT - 20,
            WINDOW_WIDTH / 2 - PLAYER_WIDTH / 2,
            WINDOW_HEIGHT - 20,
            WINDOW_WIDTH / 2 + PLAYER_WIDTH / 2,
            WINDOW_HEIGHT - 20,
            fill="white",
        )
        self.x_speed = 0

    def start_move_left(self, event):
        """Starts moving left."""
        self.x_speed = -PLAYER_SPEED

    def start_move_right(self, event):
        """Starts moving right."""
        self.x_speed = PLAYER_SPEED

    def stop_move(self, event):
        """Stops horizontal movement."""
        self.x_speed = 0

    def update(self):
        """Moves the player horizontally and stops at the window edges."""
        self.canvas.move(self.id, self.x_speed, 0)
        pos = self.canvas.bbox(self.id)
        if not pos:
            return
        if pos[0] <= 0:
            self.canvas.move(self.id, -pos[0], 0)
        elif pos[2] >= WINDOW_WIDTH:
            self.canvas.move(self.id, WINDOW_WIDTH - pos[2], 0)


class Enemy:
    """Represents an enemy ship."""

    def __init__(self, canvas):
        self.canvas = canvas
        start_x = random.randint(0, WINDOW_WIDTH - ENEMY_WIDTH)
        self.id = self.canvas.create_polygon(
            start_x,
            -ENEMY_HEIGHT,
            start_x + ENEMY_WIDTH,
            -ENEMY_HEIGHT,
            start_x + ENEMY_WIDTH / 2,
            0,
            fill="white",
        )
        self.x_speed = random.choice([-2, 2])

    def update(self):
        """Moves the enemy downwards and diagonally, bouncing off side walls."""
        self.canvas.move(self.id, self.x_speed, ENEMY_SPEED)
        pos = self.canvas.bbox(self.id)
        if pos and (pos[0] <= 0 or pos[2] >= WINDOW_WIDTH):
            self.x_speed *= -1


class Bullet:
    """Represents a bullet fired by the player."""

    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.id = self.canvas.create_rectangle(
            x - BULLET_WIDTH / 2, y - BULLET_HEIGHT, x + BULLET_WIDTH / 2, y, fill="white"
        )

    def update(self):
        """Moves the bullet upwards."""
        self.canvas.move(self.id, 0, -BULLET_SPEED)


if __name__ == "__main__":
    game = Game()
    game.mainloop()
