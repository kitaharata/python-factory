import json

import pyxel


class App:
    def __init__(self):
        pyxel.init(160, 120, title="Pyxel Shooting", fps=60)

        pyxel.sounds[0].set("a3a2c1g1", "p", "7", "v", 5)
        pyxel.sounds[1].set("g2g1g1f1", "t", "7", "vs", 10)
        pyxel.sounds[2].set("c2c1g1g0", "n", "7", "v", 20)

        with open("1758812430.json", "r") as f:
            self.config = json.load(f)
        self.enemy_types = self.config["enemy_types"]
        self.enemy_configs = {t["type"]: t for t in self.enemy_types}

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
        self.kills = 0
        self.stage = 1
        self.init_stars()
        self.enemies_spawned = 0
        self.update_stage_config()

    def update_stage_config(self):
        """Update stage configuration from JSON."""
        stages = self.config["stages"]
        idx = min(self.stage - 1, len(stages) - 1)
        stage_cfg = stages[idx].copy()
        if self.stage > len(stages):
            extra = self.stage - len(stages)
            stage_cfg["target_spawn"] += 5 * extra
            stage_cfg["spawn_rate"] = max(10, stage_cfg["spawn_rate"] - 2 * extra)
        self.stage_config = stage_cfg
        self.bg_color = stage_cfg.get("bg_color", 0)
        self.target_spawn = self.stage_config["target_spawn"]

    def update(self):
        """Update the game logic."""
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.restart()
            return

        self.update_player()
        self.update_bullets_and_enemies()
        self.update_explosions()
        self.update_stars()

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

        spawn_rate = self.stage_config["spawn_rate"]
        available_types = self.stage_config["available_types"]
        if pyxel.frame_count % spawn_rate == 0 and self.enemies_spawned < self.target_spawn and len(self.enemies) < 5:
            x = pyxel.rndi(0, pyxel.width - 8)
            type_idx = pyxel.rndi(0, len(available_types) - 1)
            enemy_type = available_types[type_idx]
            config_type = self.enemy_configs[enemy_type]
            vy_scale = config_type["vy_scale"]
            vy_min = config_type["vy_base_min"] + self.stage * vy_scale
            vy_max = config_type["vy_base_max"] + self.stage * vy_scale
            vy = pyxel.rndf(vy_min, vy_max)
            vx_scale = config_type["vx_scale"]
            vx_min = config_type["vx_base_min"] + self.stage * vx_scale
            vx_max = config_type["vx_base_max"] + self.stage * vx_scale
            if vx_min == vx_max:
                vx = vx_min
            else:
                vx = pyxel.rndf(vx_min, vx_max)
            self.enemies.append([x, 0, vy, vx, enemy_type])
            self.enemies_spawned += 1

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
                    enemy_type = e[4]
                    config_type = self.enemy_configs[enemy_type]
                    points = config_type["points"]
                    self.score += points
                    self.kills += 1
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

        if len(self.enemies) == 0 and self.enemies_spawned >= self.target_spawn:
            self.stage += 1
            self.update_stage_config()
            self.enemies_spawned = 0
            self.init_stars()
            self.score += 500 * self.stage  # ステージクリアボーナス
            pyxel.play(0, 1)

    def update_explosions(self):
        """Update explosion effects."""
        self.explosions = [ex for ex in self.explosions if ex[2] < 15]
        for ex in self.explosions:
            ex[2] += 1

    def init_stars(self):
        """Initialize starfield for current stage."""
        self.stars = []
        num_stars = 40 + self.stage * 5
        speed_inc = 0.1 * (self.stage - 1)
        for _ in range(num_stars):
            self.stars.append(
                [
                    pyxel.rndi(0, pyxel.width - 1),
                    pyxel.rndi(0, pyxel.height - 1),
                    pyxel.rndf(0.5 + speed_inc, 1.5 + speed_inc),
                ]
            )

    def update_stars(self):
        """Update starfield."""
        for star in self.stars:
            star[1] += star[2]
            if star[1] > pyxel.height:
                star[1] = 0

    def draw(self):
        """Draw the screen."""
        pyxel.cls(self.bg_color)
        for star in self.stars:
            pyxel.pset(star[0], int(star[1]), 7)
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
            enemy_type = e[4]
            config_type = self.enemy_configs[enemy_type]
            c = config_type["color"]
            x = e[0]
            y = e[1]
            if config_type["shape"] == "tri":
                pyxel.tri(x, y, x + 8, y, x + 4, y + 8, c)
            elif config_type["shape"] == "rect":
                pyxel.rect(x, y, 8, 8, c)
            elif config_type["shape"] == "circ":
                pyxel.circ(x + 4, y + 4, 4, c)
            additional_parts = config_type.get("additional_parts", [])
            for part in additional_parts:
                px = int(x + part["rel_x"])
                py = int(y + part["rel_y"])
                part_type = part.get("type", "rect")
                c = part["color"]
                if part_type == "rect":
                    pyxel.rect(px, py, part["w"], part["h"], c)
                elif part_type == "tri":
                    tip_x = px + part["w"] // 2
                    base_y = py + part["h"]
                    pyxel.tri(px, base_y, px + part["w"], base_y, tip_x, py, c)
                elif part_type == "tri_down":
                    tip_x = px + part["w"] // 2
                    tip_y = py + part["h"]
                    pyxel.tri(px, py, px + part["w"], py, tip_x, tip_y, c)

        for ex in self.explosions:
            frame = ex[2]
            color = 7 if frame < 5 else (10 if frame < 10 else 9)
            radius = frame / 2
            pyxel.circb(ex[0] + 4, ex[1] + 4, radius, color)
        pyxel.text(5, 5, f"SCORE: {self.score:05}", 7)
        pyxel.text(5, 15, f"LIVES: {self.lives}", 7)
        pyxel.text(5, 25, f"STAGE: {self.stage}", 7)

        if self.game_over:
            pyxel.text(pyxel.width / 2 - 24, pyxel.height / 2 - 8, "GAME OVER", pyxel.frame_count % 16)
            pyxel.text(pyxel.width / 2 - 44, pyxel.height / 2 + 4, "PRESS ENTER TO RESTART", 7)


App()
