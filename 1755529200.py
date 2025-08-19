import pyxel


class App:
    def __init__(self):
        pyxel.init(160, 120, title="Pyxel Shooting", fps=60)

        pyxel.sounds[0].set("a3a2c1g1", "p", "7", "v", 5)
        pyxel.sounds[1].set("g2g1g1f1", "t", "7", "vs", 10)
        pyxel.sounds[2].set("c2c1g1g0", "n", "7", "v", 20)

        self.restart()
        pyxel.run(self.update, self.draw)

    def restart(self):
        """Initialize the game state."""
        self.player_x = 76
        self.player_y = 110
        self.player_w = 8
        self.player_h = 8

        self.bullets = []
        self.enemies = []
        self.explosions = []

        self.score = 0
        self.lives = 3
        self.game_over = False

    def update(self):
        """Update the game logic."""
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.restart()
            return

        self.update_player()
        self.update_bullets_and_enemies()
        self.update_explosions()

    def update_player(self):
        """Update the player's state."""
        if pyxel.btn(pyxel.KEY_LEFT):
            self.player_x = max(self.player_x - 2, 0)
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.player_x = min(self.player_x + 2, pyxel.width - self.player_w)

        if pyxel.btnp(pyxel.KEY_SPACE):
            self.bullets.append([self.player_x + self.player_w / 2 - 1, self.player_y])
            pyxel.play(0, 0)

    def update_bullets_and_enemies(self):
        """Update bullets and enemies, and perform collision detection."""
        bullet_w, bullet_h = 2, 4
        enemy_w, enemy_h = 8, 8

        for b in self.bullets:
            b[1] -= 4

        if pyxel.frame_count % 30 == 0:
            vy = pyxel.rndf(0.5, 1.5)
            vx = pyxel.rndf(-1.0, 1.0)
            self.enemies.append([pyxel.rndi(0, pyxel.width - enemy_w), 0, vy, vx])

        for e in self.enemies:
            e[0] += e[3]
            e[1] += e[2]
            if e[0] < 0 or e[0] + enemy_w > pyxel.width:
                e[3] *= -1

        bullets_hit = set()
        enemies_hit = set()

        for i, b in enumerate(self.bullets):
            for j, e in enumerate(self.enemies):
                if (
                    b[0] < e[0] + enemy_w
                    and b[0] + bullet_w > e[0]
                    and b[1] < e[1] + enemy_h
                    and b[1] + bullet_h > e[1]
                ):
                    bullets_hit.add(i)
                    enemies_hit.add(j)
                    self.score += 100
                    self.explosions.append([e[0], e[1], 0])
                    pyxel.play(0, 1)

        for j, e in enumerate(self.enemies):
            if j in enemies_hit:
                continue

            # Player-enemy collision
            if (
                self.player_x < e[0] + enemy_w
                and self.player_x + self.player_w > e[0]
                and self.player_y < e[1] + enemy_h
                and self.player_y + self.player_h > e[1]
            ):
                enemies_hit.add(j)  # Mark enemy as hit
                self.lives -= 1
                self.explosions.append([self.player_x, self.player_y, 0])
                pyxel.play(0, 2)

                if self.lives <= 0:
                    self.game_over = True
                    break

        if self.game_over:
            return
        self.bullets = [b for i, b in enumerate(self.bullets) if i not in bullets_hit and b[1] > -bullet_h]
        self.enemies = [e for j, e in enumerate(self.enemies) if j not in enemies_hit and e[1] < pyxel.height]

    def update_explosions(self):
        """Update explosion effects."""
        self.explosions = [ex for ex in self.explosions if ex[2] < 15]
        for ex in self.explosions:
            ex[2] += 1

    def draw(self):
        """Draw the screen."""
        pyxel.cls(1)
        pyxel.tri(
            self.player_x,
            self.player_y + self.player_h,
            self.player_x + self.player_w,
            self.player_y + self.player_h,
            self.player_x + self.player_w / 2,
            self.player_y,
            11,
        )
        for b in self.bullets:
            pyxel.rect(b[0], b[1], 2, 4, 7)

        for e in self.enemies:
            pyxel.tri(e[0], e[1], e[0] + 8, e[1], e[0] + 4, e[1] + 8, 8)

        for ex in self.explosions:
            frame = ex[2]
            color = 7 if frame < 5 else (10 if frame < 10 else 9)
            radius = frame / 2
            pyxel.circb(ex[0] + 4, ex[1] + 4, radius, color)
        pyxel.text(5, 5, f"SCORE: {self.score:05}", 7)
        pyxel.text(5, 15, f"LIVES: {self.lives}", 7)

        if self.game_over:
            pyxel.text(pyxel.width / 2 - 24, pyxel.height / 2 - 8, "GAME OVER", pyxel.frame_count % 16)
            pyxel.text(pyxel.width / 2 - 44, pyxel.height / 2 + 4, "PRESS ENTER TO RESTART", 7)


App()
