import json
from enum import Enum

import pyxel


class GameState(Enum):
    IDLE = "IDLE"
    MESSAGE = "MESSAGE"
    CHOICE = "CHOICE"
    BATTLE_MENU = "BATTLE_MENU"
    BATTLE_PLAYER_ATTACK = "BATTLE_PLAYER_ATTACK"
    BATTLE_ITEM_USED = "BATTLE_ITEM_USED"
    BATTLE_ENEMY_ATTACK = "BATTLE_ENEMY_ATTACK"
    ITEM_GET = "ITEM_GET"
    STATUS = "STATUS"
    GAME_OVER = "GAME_OVER"


class BattlePhase(Enum):
    PLAYER_TURN = "PLAYER_TURN"
    ENEMY_TURN = "ENEMY_TURN"
    BATTLE_END_WIN = "BATTLE_END_WIN"
    BATTLE_END_LOSE = "BATTLE_END_LOSE"


class GameManager:
    def __init__(self, game_data):
        self.game_data = game_data
        self.player = {}
        self.game_state = GameState.IDLE
        self.current_event_id = "start_game"
        self.current_event = None
        self.message_queue = []
        self.choice_selected_index = 0
        self.current_enemy = None
        self.battle_log = []
        self.battle_phase = None
        self.battle_menu_selected_index = 0

        self._initialize_player_state()
        self._start_event(self.current_event_id)

    def _initialize_player_state(self):
        self.player = self.game_data["player_initial_stats"].copy()
        self.player["inventory"] = {}
        self.player["equipment"] = {"weapon": None, "armor": None}
        for item_data in self.game_data["items"]:
            if item_data["id"] == "sword" and item_data["type"] == "weapon":
                self.player["equipment"]["weapon"] = item_data["id"]
                if "attack_boost" in item_data["effect"]:
                    self.player["attack"] += item_data["effect"]["attack_boost"]
                break

    def _get_event(self, event_id):
        for event in self.game_data["events"]:
            if event["id"] == event_id:
                return event
        return None

    def _get_item(self, item_id):
        for item in self.game_data["items"]:
            if item["id"] == item_id:
                return item
        return None

    def _get_enemy(self, enemy_id):
        for enemy in self.game_data["enemies"]:
            if enemy["id"] == enemy_id:
                return enemy
        return None

    def _start_event(self, event_id):
        self.current_event_id = event_id
        event = self._get_event(event_id)
        if not event:
            self.message_queue = [f"Error: Event '{event_id}' not found."]
            self.game_state = GameState.GAME_OVER
            return
        self.current_event = event
        self.message_queue = [event["message"]]
        self.choice_selected_index = 0
        self.battle_log = []
        if event["type"] == "message":
            self.game_state = GameState.MESSAGE

        elif event["type"] == "choice":
            self.game_state = GameState.CHOICE

        elif event["type"] == "battle":
            self.current_enemy = self._get_enemy(event["enemy_id"]).copy()
            self.battle_log.append(event["message"])
            self.battle_log.append(f"{self.current_enemy['name']} appeared!")
            self.battle_phase = BattlePhase.PLAYER_TURN
            self.game_state = GameState.BATTLE_MENU

        elif event["type"] == "item_get":
            item = self._get_item(event["item_id"])
            if item:
                quantity = event.get("quantity", 1)
                self._add_item_to_inventory(item["id"], quantity)
                self.message_queue.append(f"Got {quantity} {item['name']}!")
            self.game_state = GameState.ITEM_GET

        elif event["type"] == "status":
            self.game_state = GameState.STATUS

        elif event["id"] == "game_over_final":
            self.game_state = GameState.GAME_OVER

    def _add_item_to_inventory(self, item_id, quantity):
        if item_id in self.player["inventory"]:
            self.player["inventory"][item_id] += quantity
        else:
            self.player["inventory"][item_id] = quantity

    def _use_item(self, item_id):
        item = self._get_item(item_id)
        if not item:
            self.battle_log.append(f"Item '{item_id}' not found!")
            return False
        if item_id not in self.player["inventory"] or self.player["inventory"][item_id] <= 0:
            self.battle_log.append(f"You don't have {item['name']}!")
            return False
        if item["type"] != "consumable":
            self.battle_log.append(f"{item['name']} cannot be used!")
            return False
        if "hp_restore" in item["effect"]:
            heal_amount = item["effect"]["hp_restore"]
            self.player["hp"] = min(self.player["max_hp"], self.player["hp"] + heal_amount)
            self.player["inventory"][item_id] -= 1
            self.battle_log.append(f"Used {item['name']}! HP recovered by {heal_amount}!")
            return True
        return False

    def _handle_player_attack(self):
        player_attack = self.player["attack"]
        enemy_defense = self.current_enemy["defense"]
        damage = max(1, player_attack - enemy_defense)
        self.current_enemy["hp"] -= damage
        self.battle_log.append(f"Player attacks! {self.current_enemy['name']} takes {damage} damage!")
        if self._check_battle_end():
            return
        self.battle_phase = BattlePhase.ENEMY_TURN

    def _handle_enemy_attack(self):
        enemy_attack = self.current_enemy["attack"]
        player_defense = self.player["defense"]
        damage = max(1, enemy_attack - player_defense)
        self.player["hp"] -= damage
        self.battle_log.append(f"{self.current_enemy['name']} attacks! Player takes {damage} damage!")
        if self._check_battle_end():
            return
        self.battle_phase = BattlePhase.PLAYER_TURN
        self.game_state = GameState.BATTLE_MENU

    def _check_battle_end(self):
        if self.current_enemy["hp"] <= 0:
            self.battle_log.append(f"Defeated {self.current_enemy['name']}!")
            self.battle_phase = BattlePhase.BATTLE_END_WIN
            return True
        if self.player["hp"] <= 0:
            self.battle_log.append("Player has fallen...")
            self.battle_phase = BattlePhase.BATTLE_END_LOSE
            return True
        return False

    def _end_battle(self, outcome_type):
        if outcome_type == BattlePhase.BATTLE_END_WIN:
            self.player["exp"] += self.current_enemy["reward_exp"]
            self.player["gold"] += self.current_enemy["reward_gold"]
            self.battle_log.append(
                f"Gained {self.current_enemy['reward_exp']} EXP and {self.current_enemy['reward_gold']} gold!"
            )
            self._check_level_up()
            next_event_id = self.current_event["on_win"]["next_event"]
        else:
            next_event_id = self.current_event["on_lose"]["next_event"]
        self.current_enemy = None
        self._start_event(next_event_id)

    def _check_level_up(self):
        while self.player["exp"] >= self.player["level"] * 100:
            self.player["exp"] -= self.player["level"] * 100
            self.player["level"] += 1
            self.player["max_hp"] += 10
            self.player["hp"] = self.player["max_hp"]
            self.player["attack"] += 2
            self.player["defense"] += 1
            self.battle_log.append(f"Level Up! Reached level {self.player['level']}!")

    def handle_z_press(self):
        if (
            self.game_state == GameState.MESSAGE
            or self.game_state == GameState.ITEM_GET
            or self.game_state == GameState.STATUS
        ):
            if len(self.message_queue) > 1:
                self.message_queue.pop(0)
            else:
                next_event_id = self.current_event.get("next_event")
                if next_event_id:
                    self._start_event(next_event_id)
                elif "choices" in self.current_event:
                    self.game_state = GameState.CHOICE
        elif self.game_state == GameState.CHOICE:
            selected_choice = self.current_event["choices"][self.choice_selected_index]["outcome"]
            if "message" in selected_choice:
                self.message_queue = [selected_choice["message"]]
                self.game_state = GameState.MESSAGE
            next_event_id = selected_choice.get("next_event")
            if next_event_id:
                self._start_event(next_event_id)

        elif self.game_state == GameState.BATTLE_MENU:
            if self.battle_menu_selected_index == 0:
                self.game_state = GameState.BATTLE_PLAYER_ATTACK
                self._handle_player_attack()
            elif self.battle_menu_selected_index == 1:
                if self._use_item("potion"):
                    self.game_state = GameState.BATTLE_ITEM_USED
                    self.battle_phase = BattlePhase.ENEMY_TURN
                else:
                    self.game_state = GameState.BATTLE_MENU

        elif self.game_state == GameState.BATTLE_PLAYER_ATTACK or self.game_state == GameState.BATTLE_ITEM_USED:
            if self.battle_phase == BattlePhase.ENEMY_TURN:
                if not self._check_battle_end():
                    self.game_state = GameState.BATTLE_ENEMY_ATTACK
                    self._handle_enemy_attack()
            elif self.battle_phase == BattlePhase.BATTLE_END_WIN or self.battle_phase == BattlePhase.BATTLE_END_LOSE:
                self._end_battle(self.battle_phase)

        elif self.game_state == GameState.BATTLE_ENEMY_ATTACK:
            if self.battle_phase == BattlePhase.PLAYER_TURN:
                self.game_state = GameState.BATTLE_MENU
            elif self.battle_phase == BattlePhase.BATTLE_END_WIN or self.battle_phase == BattlePhase.BATTLE_END_LOSE:
                self._end_battle(self.battle_phase)

        elif self.game_state == GameState.GAME_OVER:
            pass

    def move_choice_selection(self, direction):
        if self.game_state == GameState.CHOICE:
            num_choices = len(self.current_event["choices"])
            if direction == "up":
                self.choice_selected_index = (self.choice_selected_index - 1 + num_choices) % num_choices
            elif direction == "down":
                self.choice_selected_index = (self.choice_selected_index + 1) % num_choices

    def move_battle_menu_selection(self, direction):
        if self.game_state == GameState.BATTLE_MENU:
            num_actions = 2
            if direction == "up":
                self.battle_menu_selected_index = (self.battle_menu_selected_index - 1 + num_actions) % num_actions
            elif direction == "down":
                self.battle_menu_selected_index = (self.battle_menu_selected_index + 1) % num_actions

    def get_player_stats(self):
        return self.player

    def get_game_state(self):
        return self.game_state

    def get_current_event(self):
        return self.current_event

    def get_message_queue(self):
        return self.message_queue

    def get_choice_selected_index(self):
        return self.choice_selected_index

    def get_current_enemy(self):
        return self.current_enemy

    def get_battle_log(self):
        return self.battle_log

    def get_battle_menu_selected_index(self):
        return self.battle_menu_selected_index

    def get_battle_phase(self):
        return self.battle_phase

    def get_item_details(self, item_id):
        return self._get_item(item_id)


class App:
    def __init__(self):
        pyxel.init(256, 192, title="RPG")
        self._load_and_display_rules()
        game_data = self._load_game_data_from_file()
        self.game_manager = GameManager(game_data)
        pyxel.run(self.update, self.draw)

    def _load_game_data_from_file(self):
        try:
            with open("1755788420.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Error: 1755788420.json not found.")
            pyxel.quit()
        except json.JSONDecodeError:
            print("Error: Failed to decode 1755788420.json. Check JSON format.")
            pyxel.quit()

    def _load_and_display_rules(self):
        try:
            with open("1755788440.txt", "r", encoding="utf-8") as f:
                rules = f.read()
                print("--- How to Play ---")
                print(rules)
                print("-------------------")
        except FileNotFoundError:
            print("Error: 1755788440.txt (rules) not found.")
        except Exception as e:
            print(f"Error loading rules: {e}")

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        game_state = self.game_manager.get_game_state()
        if game_state == GameState.GAME_OVER:
            if pyxel.btnp(pyxel.KEY_Z):
                pyxel.quit()
            return
        if pyxel.btnp(pyxel.KEY_Z):
            self.game_manager.handle_z_press()
        game_state = self.game_manager.get_game_state()
        if game_state == GameState.CHOICE:
            if pyxel.btnp(pyxel.KEY_UP):
                self.game_manager.move_choice_selection("up")
            if pyxel.btnp(pyxel.KEY_DOWN):
                self.game_manager.move_choice_selection("down")
        elif game_state == GameState.BATTLE_MENU:
            if pyxel.btnp(pyxel.KEY_UP):
                self.game_manager.move_battle_menu_selection("up")
            if pyxel.btnp(pyxel.KEY_DOWN):
                self.game_manager.move_battle_menu_selection("down")

    def _wrap_text(self, text, max_chars_per_line):
        wrapped_lines = []
        if not text:
            return [""]
        words = text.split(" ")
        current_line = ""
        for word in words:
            if current_line:
                if len(current_line) + 1 + len(word) > max_chars_per_line:
                    wrapped_lines.append(current_line)
                    current_line = word
                else:
                    current_line += " " + word
            else:
                current_line = word
        if current_line:
            wrapped_lines.append(current_line)
        return wrapped_lines

    def draw(self):
        pyxel.cls(0)
        player_stats = self.game_manager.get_player_stats()
        game_state = self.game_manager.get_game_state()
        current_event = self.game_manager.get_current_event()
        message_queue = self.game_manager.get_message_queue()
        choice_selected_index = self.game_manager.get_choice_selected_index()
        current_enemy = self.game_manager.get_current_enemy()
        battle_log = self.game_manager.get_battle_log()
        battle_menu_selected_index = self.game_manager.get_battle_menu_selected_index()
        battle_phase = self.game_manager.get_battle_phase()

        pyxel.text(5, 5, f"HP: {player_stats['hp']}/{player_stats['max_hp']}", 7)
        pyxel.text(5, 15, f"ATK: {player_stats['attack']} DEF: {player_stats['defense']}", 7)
        pyxel.text(5, 25, f"Gold: {player_stats['gold']} EXP: {player_stats['exp']} Lvl: {player_stats['level']}", 7)
        pyxel.line(0, 35, pyxel.width, 35, 13)

        y_offset = 45
        main_text_max_chars = 50
        indented_text_max_chars = 48
        if game_state == GameState.MESSAGE or game_state == GameState.ITEM_GET or game_state == GameState.STATUS:
            display_lines = []
            for msg in message_queue:
                display_lines.extend(self._wrap_text(msg, main_text_max_chars))
            current_y = y_offset
            for line in display_lines:
                pyxel.text(5, current_y, line, 7)
                current_y += 10
            if current_event and current_event.get("type") == "status":
                current_y += 10
                pyxel.text(5, current_y, f"Attack: {player_stats['attack']}", 7)
                current_y += 10
                pyxel.text(5, current_y, f"Defense: {player_stats['defense']}", 7)
                current_y += 10
                pyxel.text(5, current_y, "Inventory:", 7)
                current_y += 10
                if not player_stats["inventory"]:
                    pyxel.text(15, current_y, "None", 7)
                    current_y += 10
                else:
                    for item_id, quantity in player_stats["inventory"].items():
                        item = self.game_manager.get_item_details(item_id)
                        if item:
                            item_display_text = f"- {item['name']} x {quantity}"
                            wrapped_item_lines = self._wrap_text(item_display_text, indented_text_max_chars)
                            for line in wrapped_item_lines:
                                pyxel.text(15, current_y, line, 7)
                                current_y += 10
            pyxel.rect(0, pyxel.height - 16, pyxel.width, 16, 5)
            pyxel.text(5, pyxel.height - 10, "Press Z to proceed", 7)
        elif game_state == GameState.CHOICE:
            current_y = y_offset
            event_message_lines = self._wrap_text(current_event["message"], main_text_max_chars)
            for line in event_message_lines:
                pyxel.text(5, current_y, line, 7)
                current_y += 10
            current_y += 10
            for i, choice in enumerate(current_event["choices"]):
                color = 7
                is_selected = i == choice_selected_index
                if is_selected:
                    color = 10
                choice_text_max_chars = indented_text_max_chars - (2 if is_selected else 0)
                wrapped_choice_lines = self._wrap_text(choice["text"], choice_text_max_chars)
                for j, line in enumerate(wrapped_choice_lines):
                    if j == 0 and is_selected:
                        pyxel.text(15, current_y, f"> {line}", color)
                    elif j == 0:
                        pyxel.text(15, current_y, line, color)
                    else:
                        pyxel.text(25, current_y, line, color)
                    current_y += 10
            pyxel.rect(0, pyxel.height - 16, pyxel.width, 16, 5)
            pyxel.text(5, pyxel.height - 10, "Press Z to confirm", 7)
        elif game_state.name.startswith("BATTLE") and current_enemy:
            pyxel.text(pyxel.width - 50, 5, f"{current_enemy['name']}", 7)
            pyxel.text(pyxel.width - 50, 15, f"HP: {current_enemy['hp']}", 7)
            pyxel.line(0, 35, pyxel.width, 35, 13)
            max_log_lines_display = ((pyxel.height - 40 - 10) - y_offset) // 10
            if max_log_lines_display < 1:
                max_log_lines_display = 1
            all_wrapped_log_lines = []
            for entry in battle_log:
                all_wrapped_log_lines.extend(self._wrap_text(entry, main_text_max_chars))
            log_display_lines = all_wrapped_log_lines[-max_log_lines_display:]
            current_y = y_offset
            for line in log_display_lines:
                pyxel.text(5, current_y, line, 7)
                current_y += 10
            if game_state == GameState.BATTLE_MENU:
                pyxel.text(5, pyxel.height - 40, "Choose action:", 7)
                actions = ["Attack", "Item"]
                for i, action in enumerate(actions):
                    color = 7
                    if i == battle_menu_selected_index:
                        color = 10
                    pyxel.text(
                        15,
                        pyxel.height - 30 + i * 10,
                        f"> {action}" if i == battle_menu_selected_index else action,
                        color,
                    )
                pyxel.rect(0, pyxel.height - 16, pyxel.width, 16, 5)
                pyxel.text(5, pyxel.height - 10, "Press Z to confirm", 7)
            elif battle_phase == BattlePhase.BATTLE_END_WIN or battle_phase == BattlePhase.BATTLE_END_LOSE:
                pyxel.rect(0, pyxel.height - 16, pyxel.width, 16, 5)
                pyxel.text(5, pyxel.height - 10, "Press Z to proceed", 7)
            elif battle_phase == BattlePhase.ENEMY_TURN and game_state != GameState.BATTLE_ENEMY_ATTACK:
                pyxel.rect(0, pyxel.height - 16, pyxel.width, 16, 5)
                pyxel.text(5, pyxel.height - 10, "Press Z to proceed", 7)
            elif game_state == GameState.BATTLE_ENEMY_ATTACK:
                pyxel.rect(0, pyxel.height - 16, pyxel.width, 16, 5)
                pyxel.text(5, pyxel.height - 10, "Press Z to proceed", 7)
        elif game_state == GameState.GAME_OVER:
            pyxel.text(pyxel.width // 2 - 40, pyxel.height // 2, "GAME OVER", 8)
            pyxel.rect(0, pyxel.height - 16, pyxel.width, 16, 5)
            pyxel.text(5, pyxel.height - 10, "Press Z to quit", 7)


App()
