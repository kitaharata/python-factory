import json
from abc import ABC, abstractmethod
from enum import Enum, auto

import pyxel


class BattlePhaseActionStrategy(ABC):
    def __init__(self, game_manager):
        self.game_manager = game_manager

    @abstractmethod
    def execute(self):
        pass


class PlayerTurnActionStrategy(BattlePhaseActionStrategy):
    def execute(self):
        self.game_manager.set_state(GameState.BATTLE_MENU)


class EnemyTurnActionStrategy(BattlePhaseActionStrategy):
    def execute(self):
        if not self.game_manager._check_battle_end():
            self.game_manager.set_state(GameState.BATTLE_ENEMY_ATTACK)
            self.game_manager._handle_enemy_attack()


class BattleEndActionStrategy(BattlePhaseActionStrategy):
    def execute(self):
        self.game_manager._end_battle(self.game_manager.battle_phase)


class BattlePhase(Enum):
    def __new__(cls, value, strategy_class):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.strategy_class = strategy_class
        return obj

    PLAYER_TURN = (auto(), PlayerTurnActionStrategy)
    ENEMY_TURN = (auto(), EnemyTurnActionStrategy)
    BATTLE_END_WIN = (auto(), BattleEndActionStrategy)
    BATTLE_END_LOSE = (auto(), BattleEndActionStrategy)
    BATTLE_ITEM_USED = (auto(), EnemyTurnActionStrategy)

    @property
    def strategy(self):
        return self.strategy_class


class EventStrategy(ABC):
    def __init__(self, game_manager):
        self.game_manager = game_manager

    @abstractmethod
    def execute(self, event, temp_enemy_id=None):
        pass


class MessageEventStrategy(EventStrategy):
    def execute(self, event, temp_enemy_id=None):
        self.game_manager.message_queue = [event["message"]]
        self.game_manager.set_state(GameState.MESSAGE)
        if "next_event" in event:
            self.game_manager._pending_next_event_id = event["next_event"]


class ChoiceEventStrategy(EventStrategy):
    def execute(self, event, temp_enemy_id=None):
        self.game_manager.set_state(GameState.CHOICE)


class BattleEventStrategy(EventStrategy):
    def execute(self, event, temp_enemy_id=None):
        enemy_to_fight_id = temp_enemy_id if temp_enemy_id else event["enemy_id"]
        self.game_manager.current_enemy = self.game_manager._get_enemy(enemy_to_fight_id).copy()
        self.game_manager.message_queue = [event["message"]]
        self.game_manager.message_queue.append(f"{self.game_manager.current_enemy['name']} appeared!")
        self.game_manager.battle_phase = BattlePhase.PLAYER_TURN
        self.game_manager.set_state(GameState.BATTLE_MENU)


class ItemGetEventStrategy(EventStrategy):
    def execute(self, event, temp_enemy_id=None):
        item = self.game_manager._get_item(event["item_id"])
        if item:
            quantity = event.get("quantity", 1)
            self.game_manager._add_item_to_inventory(item["id"], quantity)
            self.game_manager.message_queue = [event["message"], f"Obtained {quantity} {item['name']}!"]
        else:
            self.game_manager.message_queue = [f"Error: Item '{event['item_id']}' not found for item_get event."]
        self.game_manager.set_state(GameState.MESSAGE)


class StatusEventStrategy(EventStrategy):
    def execute(self, event, temp_enemy_id=None):
        self.game_manager.message_queue = [event["message"]]
        self.game_manager.set_state(GameState.MESSAGE)
        if "next_event" in event:
            self.game_manager._pending_next_event_id = event["next_event"]


class DungeonInitializerEventStrategy(EventStrategy):
    def execute(self, event, temp_enemy_id=None):
        self.game_manager.current_dungeon_id = event["dungeon_id"]
        self.game_manager.current_dungeon_distance = event["initial_distance"]
        self.game_manager.current_dungeon_initial_distance = event["initial_distance"]
        self.game_manager.current_dungeon_boss_event_id = event["boss_event_id"]
        self.game_manager.current_dungeon_normal_enemies = event["normal_enemies"]
        self.game_manager.current_dungeon_items = event.get("dungeon_items", [])
        self.game_manager.current_dungeon_win_event = event["on_win_dungeon"]
        self.game_manager.current_dungeon_lose_event = event["on_lose_dungeon"]
        self.game_manager.message_queue = [event["message"]]
        self.game_manager.set_state(GameState.MESSAGE)
        if "next_event" in event:
            self.game_manager.current_event["next_event_after_message"] = event["next_event"]


class DungeonProgressEventStrategy(EventStrategy):
    def execute(self, event, temp_enemy_id=None):
        if self.game_manager.current_dungeon_id is None:
            self.game_manager.message_queue = ["Error: 'dungeon_progress' event called outside a dungeon."]
            self.game_manager.game_state = GameState.GAME_OVER
            return
        self.game_manager.current_dungeon_distance -= 1
        self.game_manager.message_queue = [event["message"]]
        if self.game_manager.current_dungeon_distance == 0:
            self.game_manager.message_queue.append("Feeling a formidable presence in the depths! It's the boss!")
            self.game_manager._pending_next_event_id = self.game_manager.current_dungeon_boss_event_id
            self.game_manager.set_state(GameState.MESSAGE)
        elif self.game_manager.current_dungeon_distance > 0:
            outcome_roll = pyxel.rndi(1, 100)
            explore_choice_event_id = self.game_manager.current_dungeon_id + "_explore_choice"
            if outcome_roll <= 60:
                random_enemy_id = self.game_manager.current_dungeon_normal_enemies[
                    pyxel.rndi(0, len(self.game_manager.current_dungeon_normal_enemies) - 1)
                ]
                enemy_name = self.game_manager._get_enemy(random_enemy_id)["name"]
                self.game_manager.message_queue.append(f"{enemy_name} appeared!")
                self.game_manager._pending_next_event_id = "dungeon_random_battle"
                self.game_manager._pending_temp_enemy_id = random_enemy_id
                self.game_manager.set_state(GameState.MESSAGE)
            elif outcome_roll <= 80:
                self.game_manager.message_queue.append("You search around for items...")
                if not self.game_manager.current_dungeon_items:
                    self.game_manager.message_queue.append("But find nothing.")
                else:
                    random_item_id = self.game_manager.current_dungeon_items[
                        pyxel.rndi(0, len(self.game_manager.current_dungeon_items) - 1)
                    ]
                    quantity = 1
                    item = self.game_manager._get_item(random_item_id)
                    if item:
                        self.game_manager._add_item_to_inventory(item["id"], quantity)
                        self.game_manager.message_queue.append(f"Obtained {quantity} {item['name']}!")
                    else:
                        self.game_manager.message_queue.append(f"Error: Item '{random_item_id}' not found.")
                self.game_manager._pending_next_event_id = explore_choice_event_id
                self.game_manager.set_state(GameState.MESSAGE)
            else:
                self.game_manager.message_queue.append(
                    "You rest for a moment, but nothing out of the ordinary happens."
                )
                self.game_manager._pending_next_event_id = explore_choice_event_id
                self.game_manager.set_state(GameState.MESSAGE)
        else:
            self.game_manager.message_queue.append("Error: Invalid dungeon distance.")
            self.game_manager.game_state = GameState.GAME_OVER
            return


class DungeonRetreatLogicEventStrategy(EventStrategy):
    def execute(self, event, temp_enemy_id=None):
        self.game_manager.current_dungeon_distance = min(
            self.game_manager.current_dungeon_initial_distance, self.game_manager.current_dungeon_distance + 1
        )
        self.game_manager.message_queue = [event["message"]]
        explore_choice_event_id = self.game_manager.current_dungeon_id + "_explore_choice"
        if self.game_manager.current_dungeon_distance >= self.game_manager.current_dungeon_initial_distance:
            self.game_manager.message_queue.append("Returned to the dungeon entrance.")
            self.game_manager._pending_next_event_id = "town_return"
            self.game_manager.set_state(GameState.MESSAGE)
        else:
            outcome_roll = pyxel.rndi(1, 100)
            if outcome_roll <= 60:
                random_enemy_id = self.game_manager.current_dungeon_normal_enemies[
                    pyxel.rndi(0, len(self.game_manager.current_dungeon_normal_enemies) - 1)
                ]
                enemy_name = self.game_manager._get_enemy(random_enemy_id)["name"]
                self.game_manager.message_queue.append(f"{enemy_name} appeared!")
                self.game_manager._pending_next_event_id = "dungeon_random_battle"
                self.game_manager._pending_temp_enemy_id = random_enemy_id
                self.game_manager.set_state(GameState.MESSAGE)
            elif outcome_roll <= 80:
                self.game_manager.message_queue.append("You search around for items...")
                if not self.game_manager.current_dungeon_items:
                    self.game_manager.message_queue.append("But find nothing.")
                else:
                    random_item_id = self.game_manager.current_dungeon_items[
                        pyxel.rndi(0, len(self.game_manager.current_dungeon_items) - 1)
                    ]
                    quantity = 1
                    item = self.game_manager._get_item(random_item_id)
                    if item:
                        self.game_manager._add_item_to_inventory(item["id"], quantity)
                        self.game_manager.message_queue.append(f"Obtained {quantity} {item['name']}!")
                    else:
                        self.game_manager.message_queue.append(f"Error: Item '{random_item_id}' not found.")
                self.game_manager._pending_next_event_id = explore_choice_event_id
                self.game_manager.set_state(GameState.MESSAGE)
            else:
                self.game_manager.message_queue.append(
                    "You rest for a moment, but nothing out of the ordinary happens."
                )
                self.game_manager._pending_next_event_id = explore_choice_event_id
                self.game_manager.set_state(GameState.MESSAGE)


class ShopTransactionEventStrategy(EventStrategy):
    def execute(self, event, temp_enemy_id=None):
        item_id = event["item_id"]
        item_to_buy = self.game_manager._get_item(item_id)
        cost = item_to_buy["price"]
        quantity = event.get("quantity", 1)
        if self.game_manager.player["gold"] >= cost:
            self.game_manager.player["gold"] -= cost
            self.game_manager._add_item_to_inventory(item_id, quantity)
            if item_to_buy["type"] == "weapon" and not self.game_manager.player["equipment"]["weapon"]:
                self.game_manager.player["equipment"]["weapon"] = item_id
                if "attack_boost" in item_to_buy["effect"]:
                    self.game_manager.player["attack"] += item_to_buy["effect"]["attack_boost"]
                self.game_manager.message_queue = [f"Purchased and equipped {quantity} {item_to_buy['name']}!"]
            else:
                self.game_manager.message_queue = [f"Purchased {quantity} {item_to_buy['name']}!"]
        else:
            self.game_manager.message_queue = ["Not enough gold!"]
        self.game_manager._pending_next_event_id = "shop_entrance"
        self.game_manager.set_state(GameState.MESSAGE)


class ShopSellTransactionEventStrategy(EventStrategy):
    def execute(self, event, temp_enemy_id=None):
        item_id = event["item_id"]
        item_to_sell = self.game_manager._get_item(item_id)
        quantity = event.get("quantity", 1)
        if not item_to_sell:
            self.game_manager.message_queue = [f"Error: Item '{item_id}' not found for selling."]
        elif (
            item_id not in self.game_manager.player["inventory"]
            or self.game_manager.player["inventory"][item_id] < quantity
        ):
            self.game_manager.message_queue = [f"You don't have {quantity} {item_to_sell['name']} to sell!"]
        else:
            sell_price = item_to_sell["price"] // 2
            total_gold_gained = sell_price * quantity
            self.game_manager._remove_item_from_inventory(item_id, quantity)
            self.game_manager.player["gold"] += total_gold_gained
            self.game_manager.message_queue = [f"Sold {quantity} {item_to_sell['name']} for {total_gold_gained} Gold!"]
        self.game_manager._pending_next_event_id = "shop_entrance"
        self.game_manager.set_state(GameState.MESSAGE)


class ShopSellMenuEventStrategy(EventStrategy):
    def execute(self, event, temp_enemy_id=None):
        choices = []
        for item_id, quantity in self.game_manager.player["inventory"].items():
            if quantity > 0:
                item_details = self.game_manager._get_item(item_id)
                if item_details and item_details["type"] not in ["weapon", "armor"]:
                    sell_price = item_details["price"] // 2
                    choices.append(
                        {
                            "text": f"{item_details['name']} x {quantity} (Sell for {sell_price}G each)",
                            "outcome": {
                                "next_event": "sell_item",
                                "item_id": item_id,
                                "quantity": 1,
                            },
                        }
                    )
        choices.append({"text": "Cancel", "outcome": {"next_event": "shop_entrance"}})
        self.game_manager.current_event["message"] = event["message"]
        self.game_manager.current_event["choices"] = choices
        self.game_manager.set_state(GameState.CHOICE)


class ShopBuyMenuEventStrategy(EventStrategy):
    def execute(self, event, temp_enemy_id=None):
        choices = []
        for item_data in self.game_manager.game_data["items"]:
            if item_data["type"] != "sellable_only":
                choices.append(
                    {
                        "text": f"{item_data['name']} ({item_data['price']}G)",
                        "outcome": {
                            "next_event": "shop_transaction",
                            "item_id": item_data["id"],
                            "quantity": 1,
                        },
                    }
                )
        choices.append({"text": "Cancel", "outcome": {"next_event": "shop_entrance"}})
        self.game_manager.current_event["message"] = event["message"]
        self.game_manager.current_event["choices"] = choices
        self.game_manager.set_state(GameState.CHOICE)


class GameOverFinalEventStrategy(EventStrategy):
    def execute(self, event, temp_enemy_id=None):
        self.game_manager.set_state(GameState.GAME_OVER)


class GameClearFinalEventStrategy(EventStrategy):
    def execute(self, event, temp_enemy_id=None):
        self.game_manager.message_queue = [event["message"]]
        self.game_manager.set_state(GameState.GAME_CLEAR)


class DefaultEventStrategy(EventStrategy):
    def execute(self, event, temp_enemy_id=None):
        self.game_manager.message_queue = [
            f"Error: Unknown event type '{event.get('type', 'N/A')}' for event ID '{event.get('id', 'N/A')}'. Setting to IDLE."
        ]
        self.game_manager.set_state(GameState.IDLE)


class EventType(Enum):
    def __new__(cls, value, strategy_class):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.strategy_class = strategy_class
        return obj

    MESSAGE = (auto(), MessageEventStrategy)
    CHOICE = (auto(), ChoiceEventStrategy)
    BATTLE = (auto(), BattleEventStrategy)
    ITEM_GET = (auto(), ItemGetEventStrategy)
    STATUS = (auto(), StatusEventStrategy)
    DUNGEON_INITIALIZER = (auto(), DungeonInitializerEventStrategy)
    DUNGEON_PROGRESS = (auto(), DungeonProgressEventStrategy)
    DUNGEON_RETREAT_LOGIC = (auto(), DungeonRetreatLogicEventStrategy)
    SHOP_TRANSACTION = (auto(), ShopTransactionEventStrategy)
    GAME_OVER_FINAL_STATE = (auto(), GameOverFinalEventStrategy)
    SHOP_SELL_TRANSACTION = (auto(), ShopSellTransactionEventStrategy)
    SHOP_SELL_MENU = (auto(), ShopSellMenuEventStrategy)
    SHOP_BUY_MENU = (auto(), ShopBuyMenuEventStrategy)
    GAME_CLEAR_FINAL_STATE = (auto(), GameClearFinalEventStrategy)
    DEFAULT = (auto(), DefaultEventStrategy)

    @property
    def strategy(self):
        return self.strategy_class


class GameStateStrategy(ABC):
    def __init__(self, game_manager):
        self.game_manager = game_manager

    @abstractmethod
    def handle_z_press(self):
        pass

    @abstractmethod
    def enter_state(self):
        pass

    @abstractmethod
    def move_selection(self):
        pass


class IdleStateStrategy(GameStateStrategy):
    def handle_z_press(self):
        pass

    def enter_state(self):
        pass

    def move_selection(self):
        pass


class MessageStateStrategy(GameStateStrategy):
    def handle_z_press(self):
        self.game_manager.message_queue.clear()
        self.game_manager._transition_from_current_event()

    def enter_state(self):
        pass

    def move_selection(self):
        pass


class ChoiceStateStrategy(GameStateStrategy):
    def handle_z_press(self):
        selected_choice = self.game_manager.current_event["choices"][self.game_manager.choice_selected_index]["outcome"]
        next_event_id_from_outcome = selected_choice.get("next_event")
        if "message" in selected_choice:
            self.game_manager.message_queue = [selected_choice["message"]]
            self.game_manager.set_state(GameState.MESSAGE)
            if next_event_id_from_outcome:
                self.game_manager.current_event["next_event_after_message"] = next_event_id_from_outcome
        elif next_event_id_from_outcome:
            extra_data_for_next_event = {k: v for k, v in selected_choice.items() if k not in ["next_event", "message"]}
            self.game_manager._start_event(next_event_id_from_outcome, extra_event_data=extra_data_for_next_event)

    def enter_state(self):
        self.game_manager.choice_selected_index = 0

    def move_selection(self, direction):
        num_choices = len(self.game_manager.current_event["choices"])
        if direction == "up":
            self.game_manager.choice_selected_index = (
                self.game_manager.choice_selected_index - 1 + num_choices
            ) % num_choices
        elif direction == "down":
            self.game_manager.choice_selected_index = (self.game_manager.choice_selected_index + 1) % num_choices


class BattleMenuStateStrategy(GameStateStrategy):
    def handle_z_press(self):
        if self.game_manager.battle_menu_selected_index == 0:
            self.game_manager.set_state(GameState.BATTLE_PLAYER_ATTACK)
            self.game_manager._handle_player_attack()
        elif self.game_manager.battle_menu_selected_index == 1:
            self.game_manager.set_state(GameState.BATTLE_ITEM_SELECTION)

    def enter_state(self):
        self.game_manager.battle_menu_selected_index = 0

    def move_selection(self, direction):
        num_actions = 2
        if direction == "up":
            self.game_manager.battle_menu_selected_index = (
                self.game_manager.battle_menu_selected_index - 1 + num_actions
            ) % num_actions
        elif direction == "down":
            self.game_manager.battle_menu_selected_index = (
                self.game_manager.battle_menu_selected_index + 1
            ) % num_actions


class BattleActionStateStrategy(GameStateStrategy):
    def __init__(self, game_manager):
        super().__init__(game_manager)

    def handle_z_press(self):
        current_phase = self.game_manager.battle_phase
        strategy_class = current_phase.strategy
        strategy_instance = strategy_class(self.game_manager)
        strategy_instance.execute()

    def enter_state(self):
        pass

    def move_selection(self):
        pass


class BattlePlayerAttackStateStrategy(BattleActionStateStrategy):
    pass


class BattleItemUsedStateStrategy(BattleActionStateStrategy):
    def handle_z_press(self):
        self.game_manager.battle_phase = BattlePhase.ENEMY_TURN
        super().handle_z_press()


class BattleItemSelectionStateStrategy(GameStateStrategy):
    def handle_z_press(self):
        selected_item_index = self.game_manager.battle_item_selected_index
        available_items = self.game_manager.get_available_battle_items()
        if selected_item_index < len(available_items):
            item_data = available_items[selected_item_index]
            if item_data["id"] == "back":
                self.game_manager.set_state(GameState.BATTLE_MENU)
            else:
                item_id = item_data["id"]
                if self.game_manager._use_item(item_id):
                    self.game_manager.set_state(GameState.BATTLE_ITEM_USED)

    def enter_state(self):
        self.game_manager.battle_item_selected_index = 0
        self.game_manager.update_available_battle_items()

    def move_selection(self, direction):
        available_items = self.game_manager.get_available_battle_items()
        num_items = len(available_items)
        if num_items == 0:
            return
        if direction == "up":
            self.game_manager.battle_item_selected_index = (
                self.game_manager.battle_item_selected_index - 1 + num_items
            ) % num_items
        elif direction == "down":
            self.game_manager.battle_item_selected_index = (
                self.game_manager.battle_item_selected_index + 1
            ) % num_items


class BattleEnemyAttackStateStrategy(BattleActionStateStrategy):
    pass


class GameOverStateStrategy(GameStateStrategy):
    def handle_z_press(self):
        pass

    def enter_state(self):
        pass

    def move_selection(self):
        pass


class DrawStrategy(ABC):
    def __init__(self, game_manager, app_instance):
        self.game_manager = game_manager
        self.app_instance = app_instance

    @abstractmethod
    def draw_screen(self):
        pass


class BaseGameDrawStrategy(DrawStrategy):
    def draw_common_elements(self):
        pyxel.cls(0)
        player_stats = self.game_manager.get_player_stats()
        pyxel.text(5, 5, f"HP: {player_stats['hp']}/{player_stats['max_hp']}", 7)
        pyxel.text(5, 15, f"ATK: {player_stats['attack']} DEF: {player_stats['defense']}", 7)
        pyxel.text(5, 25, f"Gold: {player_stats['gold']} EXP: {player_stats['exp']} Lvl: {player_stats['level']}", 7)
        if self.game_manager.current_dungeon_id:
            remaining_text = f"Remaining: {self.game_manager.current_dungeon_distance} steps"
            pyxel.text(5, 35, remaining_text, 7)
        pyxel.line(0, 45, pyxel.width, 45, 13)

    @abstractmethod
    def draw_screen(self):
        pass


class IdleDrawStrategy(BaseGameDrawStrategy):
    def draw_screen(self):
        super().draw_common_elements()


class MessageDrawStrategy(BaseGameDrawStrategy):
    def draw_screen(self):
        super().draw_common_elements()
        message_queue = self.game_manager.get_message_queue()
        current_event = self.game_manager.get_current_event()
        player_stats = self.game_manager.get_player_stats()
        y_offset = 55
        main_text_max_chars = 50
        indented_text_max_chars = 48
        current_y = y_offset
        if message_queue:
            for message in message_queue:
                display_lines = self.game_manager._wrap_text(message, main_text_max_chars)
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
                        wrapped_item_lines = self.game_manager._wrap_text(item_display_text, indented_text_max_chars)
                        for line in wrapped_item_lines:
                            pyxel.text(15, current_y, line, 7)
                            current_y += 10
        pyxel.rect(0, pyxel.height - 16, pyxel.width, 16, 5)
        pyxel.text(5, pyxel.height - 10, "Press Z to proceed", 7)


class ChoiceDrawStrategy(BaseGameDrawStrategy):
    def draw_screen(self):
        super().draw_common_elements()
        current_event = self.game_manager.get_current_event()
        choice_selected_index = self.game_manager.get_choice_selected_index()
        y_offset = 55
        main_text_max_chars = 50
        indented_text_max_chars = 48
        current_y = y_offset
        event_message_lines = self.game_manager._wrap_text(current_event["message"], main_text_max_chars)
        for line in event_message_lines:
            pyxel.text(5, current_y, line, 7)
            current_y += 10
        current_y += 10
        for i, choice in enumerate(current_event["choices"]):
            color = 7
            is_selected = i == choice_selected_index
            if is_selected:
                color = 10
            display_choice_text = choice["text"]
            if (
                self.game_manager.get_game_state() == GameState.CHOICE
                and current_event["id"] == "shop_entrance"
                and "item_id" in choice["outcome"]
            ):
                item_details = self.game_manager.get_item_details(choice["outcome"]["item_id"])
                if item_details:
                    display_choice_text = f"{item_details['name']} ({item_details['price']}G)"
            choice_text_max_chars = indented_text_max_chars - (2 if is_selected else 0)
            wrapped_choice_lines = self.game_manager._wrap_text(display_choice_text, choice_text_max_chars)
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


class BattleDrawStrategy(BaseGameDrawStrategy):
    def draw_screen(self):
        super().draw_common_elements()
        current_enemy = self.game_manager.get_current_enemy()
        battle_log = self.game_manager.get_battle_log()
        game_state = self.game_manager.get_game_state()
        battle_menu_selected_index = self.game_manager.get_battle_menu_selected_index()
        battle_phase = self.game_manager.get_battle_phase()
        y_offset = 55
        main_text_max_chars = 50
        pyxel.text(130, 5, f"{current_enemy['name']}", 7)
        pyxel.text(130, 15, f"HP: {current_enemy['hp']}", 7)
        max_log_lines_display = ((pyxel.height - 40 - 10) - y_offset) // 10
        if max_log_lines_display < 1:
            max_log_lines_display = 1
        all_wrapped_log_lines = []
        for entry in battle_log:
            all_wrapped_log_lines.extend(self.game_manager._wrap_text(entry, main_text_max_chars))
        log_display_lines = all_wrapped_log_lines[-max_log_lines_display:]
        current_y = y_offset
        for line in log_display_lines:
            pyxel.text(5, current_y, line, 7)
            current_y += 10
        if game_state == GameState.BATTLE_MENU:
            pyxel.text(5, pyxel.height - 50, "Choose action:", 7)
            actions = ["Attack", "Item"]
            for i, action in enumerate(actions):
                color = 7
                if i == battle_menu_selected_index:
                    color = 10
                pyxel.text(
                    15,
                    pyxel.height - 40 + i * 10,
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
        elif game_state == GameState.BATTLE_ITEM_SELECTION:
            pyxel.text(5, pyxel.height - 70, "Use Item:", 7)
            available_battle_items = self.game_manager.get_available_battle_items()
            item_selected_index = self.game_manager.get_battle_item_selected_index()
            display_start_y = pyxel.height - 60
            has_actual_items = False
            for item_data in available_battle_items:
                if item_data["id"] != "back":
                    has_actual_items = True
                    break
            if not has_actual_items:
                pyxel.text(15, display_start_y, "No consumable items.", 7)
                display_start_y += 10
            for i, item_data in enumerate(available_battle_items):
                color = 7
                if i == item_selected_index:
                    color = 10
                display_text = f"{item_data['name']}"
                if item_data["id"] != "back":
                    display_text += f" x {item_data['quantity']}"
                pyxel.text(
                    15,
                    display_start_y + i * 10,
                    f"> {display_text}" if i == item_selected_index else display_text,
                    color,
                )
            pyxel.rect(0, pyxel.height - 16, pyxel.width, 16, 5)
            pyxel.text(5, pyxel.height - 10, "Press Z to confirm / X to cancel", 7)


class GameOverDrawStrategy(DrawStrategy):
    def draw_screen(self):
        pyxel.cls(0)
        pyxel.text(pyxel.width // 2 - 40, pyxel.height // 2, "GAME OVER", 8)
        pyxel.rect(0, pyxel.height - 16, pyxel.width, 16, 5)
        pyxel.text(5, pyxel.height - 10, "Press Z to quit", 7)


class GameClearDrawStrategy(DrawStrategy):
    def draw_screen(self):
        pyxel.cls(0)
        text = "GAME CLEAR!"
        text_char_width = 4
        text_total_width = len(text) * text_char_width
        x = pyxel.width // 2 - text_total_width // 2
        y = pyxel.height // 2 - 3
        pyxel.text(x - 1, y - 1, text, 13)
        pyxel.text(x + 1, y + 1, text, 1)
        pyxel.text(x, y, text, 10)
        pyxel.rect(0, pyxel.height - 16, pyxel.width, 16, 5)
        pyxel.text(5, pyxel.height - 10, "Press Z to quit", 7)


class GameState(Enum):
    def __new__(cls, value, strategy_class, draw_strategy_class):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.strategy_class = strategy_class
        obj.draw_strategy_class = draw_strategy_class
        return obj

    IDLE = (auto(), IdleStateStrategy, IdleDrawStrategy)
    MESSAGE = (auto(), MessageStateStrategy, MessageDrawStrategy)
    CHOICE = (auto(), ChoiceStateStrategy, ChoiceDrawStrategy)
    BATTLE_MENU = (auto(), BattleMenuStateStrategy, BattleDrawStrategy)
    BATTLE_PLAYER_ATTACK = (auto(), BattlePlayerAttackStateStrategy, BattleDrawStrategy)
    BATTLE_ITEM_USED = (auto(), BattleItemUsedStateStrategy, BattleDrawStrategy)
    BATTLE_ITEM_SELECTION = (auto(), BattleItemSelectionStateStrategy, BattleDrawStrategy)
    BATTLE_ENEMY_ATTACK = (auto(), BattleEnemyAttackStateStrategy, BattleDrawStrategy)
    GAME_OVER = (auto(), GameOverStateStrategy, GameOverDrawStrategy)
    GAME_CLEAR = (auto(), GameOverStateStrategy, GameClearDrawStrategy)

    @property
    def strategy(self):
        return self.strategy_class

    @property
    def draw_strategy(self):
        return self.draw_strategy_class


class GameManager:
    def __init__(self, game_data):
        self.game_data = game_data
        self.player = {}
        self.game_state = GameState.IDLE
        self.current_state_strategy = None
        self.current_event_id = "start_game"
        self.current_event = None
        self.message_queue = []
        self.choice_selected_index = 0
        self.current_enemy = None
        self.battle_log = []
        self.battle_phase = None
        self.battle_menu_selected_index = 0
        self.battle_item_selected_index = 0
        self.available_battle_items = []
        self.current_dungeon_id = None
        self.current_dungeon_distance = -1
        self.current_dungeon_initial_distance = -1
        self.current_dungeon_boss_event_id = None
        self.current_dungeon_normal_enemies = []
        self.current_dungeon_items = []
        self.current_dungeon_win_event = None
        self.current_dungeon_lose_event = None
        self._pending_next_event_id = None
        self._pending_temp_enemy_id = None
        self._event_strategies = {event_type: event_type.strategy(self) for event_type in EventType}
        self._initialize_player_state()
        self._start_event(self.current_event_id)

    def set_state(self, new_state):
        self.game_state = new_state
        self.current_state_strategy = new_state.strategy(self)
        self.current_state_strategy.enter_state()

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

    def _start_event(self, event_id, temp_enemy_id=None, extra_event_data=None):
        self.current_event_id = event_id
        event = self._get_event(event_id)
        if not event:
            self.message_queue = [f"Error: Event '{event_id}' not found."]
            self.game_state = GameState.GAME_OVER
            return
        self.current_event = event.copy()
        if extra_event_data:
            self.current_event.update(extra_event_data)
        self.choice_selected_index = 0
        self.battle_log = []
        self._pending_next_event_id = None
        self._pending_temp_enemy_id = None
        if event_id == "town_return":
            self._heal_player_to_max_hp()
        event_type_str = event.get("type")
        if event_type_str:
            try:
                event_type = EventType[event_type_str.upper()]
            except KeyError:
                event_type = EventType.DEFAULT
        else:
            event_type = EventType.DEFAULT
        strategy = self._event_strategies[event_type]
        strategy.execute(self.current_event, temp_enemy_id)

    def _heal_player_to_max_hp(self):
        self.player["hp"] = self.player["max_hp"]

    def _add_item_to_inventory(self, item_id, quantity):
        if item_id in self.player["inventory"]:
            self.player["inventory"][item_id] += quantity
        else:
            self.player["inventory"][item_id] = quantity

    def _remove_item_from_inventory(self, item_id, quantity):
        if item_id in self.player["inventory"]:
            self.player["inventory"][item_id] -= quantity
            if self.player["inventory"][item_id] <= 0:
                del self.player["inventory"][item_id]

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
            self.battle_log.append(f"Used {item['name']}! Restored {heal_amount} HP!")
            return True
        return False

    def _handle_player_attack(self):
        player_attack = self.player["attack"]
        enemy_defense = self.current_enemy["defense"]
        damage = max(1, player_attack - enemy_defense)
        self.current_enemy["hp"] -= damage
        self.battle_log.append(f"Player's attack! Dealt {damage} damage to {self.current_enemy['name']}!")
        if self._check_battle_end():
            return
        self.battle_phase = BattlePhase.ENEMY_TURN

    def _handle_enemy_attack(self):
        enemy_attack = self.current_enemy["attack"]
        player_defense = self.player["defense"]
        damage = max(1, enemy_attack - player_defense)
        self.player["hp"] -= damage
        self.battle_log.append(f"{self.current_enemy['name']}'s attack! Player took {damage} damage!")
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
            self.battle_log.append("The player has fallen...")
            self.battle_phase = BattlePhase.BATTLE_END_LOSE
            return True
        return False

    def _end_battle(self, outcome_type):
        if outcome_type == BattlePhase.BATTLE_END_WIN:
            self.player["exp"] += self.current_enemy["reward_exp"]
            self.player["gold"] += self.current_enemy["reward_gold"]
            self.battle_log.append(
                f"Gained {self.current_enemy['reward_exp']} EXP and {self.current_enemy['reward_gold']} Gold!"
            )
            self._check_level_up()
            if "drop_items" in self.current_enemy and self.current_enemy["drop_items"]:
                for drop_item in self.current_enemy["drop_items"]:
                    drop_chance = drop_item.get("drop_chance", 0)
                    if pyxel.rndi(1, 100) <= drop_chance:
                        item_id = drop_item["item_id"]
                        quantity = drop_item.get("quantity", 1)
                        item_details = self._get_item(item_id)
                        if item_details:
                            self._add_item_to_inventory(item_id, quantity)
                            self.battle_log.append(f"Obtained {quantity} {item_details['name']}!")
                        else:
                            self.battle_log.append(f"Error: Dropped item '{item_id}' not found in game data.")
            next_event_id = None
            if self.current_dungeon_id and self.current_event_id == self.current_dungeon_boss_event_id:
                if self.current_enemy["id"] == "goblin_king":
                    self.battle_log.append("You have defeated the Goblin King! The world is saved!")
                    next_event_id = "game_clear_event"
                else:
                    self.battle_log.append(f"Cleared {self.current_dungeon_id}!")
                    next_event_id = self.current_dungeon_win_event
                self.current_dungeon_id = None
                self.current_dungeon_distance = -1
                self.current_dungeon_boss_event_id = None
                self.current_dungeon_normal_enemies = []
                self.current_dungeon_win_event = None
                self.current_dungeon_lose_event = None
                self.current_dungeon_initial_distance = -1
            else:
                next_event_id = self.current_event["on_win"]["next_event"]
        else:
            if self.current_dungeon_id and self.current_dungeon_lose_event:
                next_event_id = self.current_dungeon_lose_event
                self.current_dungeon_id = None
                self.current_dungeon_distance = -1
                self.current_dungeon_initial_distance = -1
                self.current_dungeon_boss_event_id = None
                self.current_dungeon_normal_enemies = []
                self.current_dungeon_win_event = None
                self.current_dungeon_lose_event = None
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
            self.battle_log.append(f"Level Up! Reached Level {self.player['level']}!")

    def _transition_from_current_event(self):
        if self._pending_next_event_id:
            next_event_id = self._pending_next_event_id
            temp_enemy_id = self._pending_temp_enemy_id
            self._pending_next_event_id = None
            self._pending_temp_enemy_id = None
            self._start_event(next_event_id, temp_enemy_id=temp_enemy_id)
            return
        if "choices" in self.current_event:
            self.set_state(GameState.CHOICE)
            return
        if self.current_dungeon_id:
            explore_choice_event_id = self.current_dungeon_id + "_explore_choice"
            self._start_event(explore_choice_event_id)
            return
        self.set_state(GameState.IDLE)

    def handle_z_press(self):
        if self.current_state_strategy:
            self.current_state_strategy.handle_z_press()

    def move_choice_selection(self, direction):
        if (
            isinstance(self.current_state_strategy, ChoiceStateStrategy)
            or isinstance(self.current_state_strategy, BattleMenuStateStrategy)
            or isinstance(self.current_state_strategy, BattleItemSelectionStateStrategy)
        ):
            self.current_state_strategy.move_selection(direction)

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

    def update_available_battle_items(self):
        self.available_battle_items = []
        for item_id, quantity in self.player["inventory"].items():
            if quantity > 0:
                item = self._get_item(item_id)
                if item and item["type"] == "consumable" and "hp_restore" in item["effect"]:
                    self.available_battle_items.append({"id": item["id"], "name": item["name"], "quantity": quantity})
        self.available_battle_items.append({"id": "back", "name": "Back", "quantity": 0})

    def get_available_battle_items(self):
        return self.available_battle_items

    def get_battle_item_selected_index(self):
        return self.battle_item_selected_index

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


class App:
    def __init__(self):
        pyxel.init(256, 192, title="RPG")
        self._load_and_display_rules()
        game_data = self._load_game_data_from_file()
        self.game_manager = GameManager(game_data)
        self._draw_strategies = {
            game_state: game_state.draw_strategy(self.game_manager, self) for game_state in GameState
        }
        pyxel.run(self.update, self.draw)

    def _load_game_data_from_file(self):
        try:
            with open("1756047620.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Error: 1756047620.json not found.")
            pyxel.quit()
        except json.JSONDecodeError:
            print("Error: Failed to decode 1756047620.json. Check JSON format.")
            pyxel.quit()

    def _load_and_display_rules(self):
        try:
            with open("1756047640.txt", "r", encoding="utf-8") as f:
                rules = f.read()
                print("--- How to Play ---")
                print(rules)
                print("-------------------")
        except FileNotFoundError:
            print("Error: 1756047640.txt (rules) not found.")
        except Exception as e:
            print(f"Error loading rules: {e}")

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        game_state = self.game_manager.get_game_state()
        if game_state == GameState.GAME_OVER or game_state == GameState.GAME_CLEAR:
            if pyxel.btnp(pyxel.KEY_Z):
                pyxel.quit()
            return
        if pyxel.btnp(pyxel.KEY_Z):
            self.game_manager.handle_z_press()
        game_state = self.game_manager.get_game_state()
        if (
            game_state == GameState.CHOICE
            or game_state == GameState.BATTLE_MENU
            or game_state == GameState.BATTLE_ITEM_SELECTION
        ):
            if pyxel.btnp(pyxel.KEY_UP):
                self.game_manager.move_choice_selection("up")
            if pyxel.btnp(pyxel.KEY_DOWN):
                self.game_manager.move_choice_selection("down")
            if game_state == GameState.BATTLE_ITEM_SELECTION and pyxel.btnp(pyxel.KEY_X):
                self.game_manager.set_state(GameState.BATTLE_MENU)

    def draw(self):
        game_state = self.game_manager.get_game_state()
        self._draw_strategies[game_state].draw_screen()


App()
