import time
import random
from domain.inventory import Inventory
from domain.item import Item


class Game:
    def __init__(self, player_name: str):
        self.player_name = player_name
        # Стартовые координаты зададим по умолчанию,
        # отрисовщик (View) сам отцентрирует их при первом рендере
        self.player_y = 10
        self.player_x = 10
        self.player_char = "☺"

        self.player_score = 0
        self.player_stage = 1
        self.player_hits = 10
        self.player_max_hits = 20
        self.player_str = 10
        self.player_agility = 10
        self.player_gold = 0
        self.player_exp = 0
        self.player_exp_to_level_up = "?"
        self.player_level = 1

        self.start_time = time.time()
        self.current_weapon = None
        self.player_total_str = self.player_str
        self.potion_effects = []

        # Внимание: инвентарь всё ещё требует stdscr. Мы почистим его позже!
        # Пока оставляем передачу None вместо stdscr, чтобы не ломать код мгновенно
        # (потребуется небольшая правка в inventory.py, если он упадет)
        self.inventory = Inventory(None, player_name, self)

        for category_name in Item.items:
            for i in range(5):
                self.inventory.category_items[category_name][i] = Item(**random.choice(Item.items[category_name]))

    def get_score(self):
        return self.player_score

    def process_turn(self, key) -> str | None:
        """Обработка одного хода/нажатия клавиши. Возвращает статус (например, 'quit') или None"""
        self.update_effects()
        self.player_score = int(time.time() - self.start_time)

        if self.player_hits <= 0:
            return "died"
        elif self.player_hits >= self.player_max_hits:
            self.player_hits = self.player_max_hits

        if key == 119 or key == 259:  # w / UP
            self.player_y -= 1
        elif key == 115 or key == 258:  # s / DOWN
            self.player_y += 1
        elif key == 97 or key == 260:  # a / LEFT
            self.player_x -= 1
        elif key == 100 or key == 261:  # d / RIGHT
            self.player_x += 1
        elif key == 105:  # i
            return "open_inventory"
        elif key == 113:  # q
            return "request_quit"

        return "continue"

    def open_category(self, category: str) -> None:
        chosen_item = self.inventory.show_category_items(category)
        if chosen_item == "Back":
            return
        if chosen_item is not None:
            category_name, slot_idx, item = chosen_item
            self.inventory.category_items[category_name][slot_idx] = None

    def update_stats(self):
        self.player_total_str = self.player_str + (self.current_weapon.value if self.current_weapon is not None else 0)

    def add_potion_effect(self, effect_type, value, duration):
        self.potion_effects.append({
            "type": effect_type,
            "value": value,
            "end_time": time.time() + duration
        })

        if effect_type == "max_hits":
            self.player_max_hits += value
            self.player_hits += value
        elif effect_type == "strength":
            self.player_str += value
        elif effect_type == "agility":
            self.player_agility += value

    def update_effects(self):
        current_time = time.time()
        all_effects = self.potion_effects.copy()
        self.potion_effects = []

        max_hp_bonus = 0
        str_bonus = 0
        agi_bonus = 0

        for effect in all_effects:
            if current_time < effect["end_time"]:
                self.potion_effects.append(effect)
            else:
                if effect["type"] == "max_hits":
                    max_hp_bonus += effect["value"]
                elif effect["type"] == "strength":
                    str_bonus += effect["value"]
                elif effect["type"] == "agility":
                    agi_bonus += effect["value"]

        self.player_max_hits -= max_hp_bonus
        self.player_hits -= max_hp_bonus
        self.player_str -= str_bonus
        self.player_agility -= agi_bonus

    def save_game_data_to_dict(self) -> dict:
        return {
            "position": [self.player_y, self.player_x],
            "player_name": self.player_name,
            "inventory": self.inventory.to_dict(),
            "score": self.player_score,
            "stage": self.player_stage,
            "player_hits": self.player_hits,
            "player_max_hits": self.player_max_hits,
            "player_str": self.player_str,
            "player_agility": self.player_agility,
            "player_gold": self.player_gold,
            "player_exp": self.player_exp,
            "player_exp_to_level_up": self.player_exp_to_level_up,
            "player_level": self.player_level,
            "start_time": self.start_time,
            "current_weapon": self.current_weapon.to_dict() if self.current_weapon else None,
            "player_total_str": self.player_total_str,
            "potion_effects": self.potion_effects
        }

    @classmethod
    def from_dict(cls, data: dict):
        game = cls.__new__(cls)
        game.player_char = "☺"
        game.player_hits = data["player_hits"]
        game.player_max_hits = data["player_max_hits"]
        game.player_name = data["player_name"]
        game.player_y, game.player_x = data["position"]
        game.player_score = data["score"]
        game.player_stage = data["stage"]
        game.player_str = data["player_str"]
        game.player_agility = data["player_agility"]
        game.player_gold = data["player_gold"]
        game.player_exp = data["player_exp"]
        game.player_exp_to_level_up = data["player_exp_to_level_up"]
        game.player_level = data["player_level"]
        game.start_time = data["start_time"]
        game.player_total_str = data.get("player_total_str", game.player_str)
        game.potion_effects = data.get("potion_effects", [])

        inv_data = data.get("inventory", {})
        game.inventory = Inventory.from_dict(None, game.player_name, game, inv_data)  # Аналогично убрали stdscr

        weapon_data = data.get("current_weapon")
        game.current_weapon = None

        if weapon_data is not None:
            game.current_weapon = Item.from_dict(weapon_data)
            for i in range(len(game.inventory.category_items["Weapon"])):
                item = game.inventory.category_items["Weapon"][i]
                if item is not None:
                    if (item.name == game.current_weapon.name and
                            item.value == game.current_weapon.value and
                            item.effect_type == game.current_weapon.effect_type):
                        game.inventory.category_items["Weapon"][i] = game.current_weapon
                        break

        game.update_stats()
        return game