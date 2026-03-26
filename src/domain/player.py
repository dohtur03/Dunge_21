import time
import random
from domain.inventory import Inventory
from domain.item import Item


class Player:
    def __init__(self, name: str, game_ref):
        self.name = name
        self.game = game_ref
        self.char = "☺"
        self.y = 0
        self.x = 0
        self.hits = 50
        self.max_hits = 50
        self.str = 10
        self.total_str = 10
        self.agility = 10
        self.gold = 0
        self.exp = 0
        self.exp_to_level_up = 50
        self.level = 1
        self.sleep_turns = 0
        self.current_weapon = None
        self.potion_effects = []
        self.inventory = Inventory(name, game_ref)

    def update_stats(self):
        # 1. Начинаем с чистой базовой силы
        current_str = self.str

        # 2. Добавляем бонусы от АКТИВНЫХ зелий (не меняя self.str!)
        for effect in self.potion_effects:
            if effect["type"] == "strength":
                current_str += effect["value"]

        # 3. Добавляем оружие
        self.total_str = current_str
        if self.current_weapon:
            self.total_str += self.current_weapon.value

    def check_level_up(self):
        if self.exp >= self.exp_to_level_up:
            self.level += 1
            self.exp -= self.exp_to_level_up
            self.exp_to_level_up = int(self.exp_to_level_up * 1.5)
            self.max_hits += 5
            self.hits = self.max_hits
            self.str += 2
            self.agility += 1
            self.update_stats()

    def add_potion_effect(self, effect_type, value, duration):
        self.potion_effects.append({
            "type": effect_type,
            "value": value,
            "end_time": time.time() + duration
        })
        self.update_stats()

    def update_effects(self):
        current_time = time.time()
        initial_count = len(self.potion_effects)

        self.potion_effects = [e for e in self.potion_effects if current_time < e["end_time"]]

        if len(self.potion_effects) != initial_count:
            self.update_stats()

    def use_item(self, category: str, slot_idx: int) -> str:
        item = self.inventory.category_items[category][slot_idx]
        if item is None: return ""

        msg = ""

        if category == "Weapon":
            if self.current_weapon is item:
                self.current_weapon = None
                msg = f"{item.name} unequipped"
            else:
                if self.current_weapon is not None:
                    old_weapon = self.current_weapon

                    drop_y, drop_x = self.y, self.x
                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
                        ny, nx = self.y + dy, self.x + dx
                        if self.game.can_move(ny, nx) and (ny, nx) not in self.game.current_level.item_drops:
                            drop_y, drop_x = ny, nx
                            break

                    # Кладем старое оружие на пол уровня
                    self.game.current_level.item_drops[(drop_y, drop_x)] = {
                        "category": "Weapon",
                        "item": old_weapon
                    }

                    for i in range(9):
                        if self.inventory.category_items["Weapon"][i] is old_weapon:
                            self.inventory.category_items["Weapon"][i] = None
                            break

                    msg = f"Swapped to {item.name}! {old_weapon.name} dropped."
                else:
                    msg = f"{item.name} equipped"

                self.current_weapon = item
            self.update_stats()

        elif category == "Food":
            old_hits = self.hits
            if old_hits == self.max_hits:
                return "HP full! You can't eat this right now."  # Защита от потери еды
            else:
                self.hits += item.value
                if self.hits >= self.max_hits:
                    msg = f"Eaten {item.name}! Restored {self.max_hits - old_hits} HP!"
                    self.hits = self.max_hits
                else:
                    msg = f"Eaten {item.name}! Restored {item.value} HP!"

                self.game.stats["food_eaten"] += 1
                self.inventory.category_items[category][slot_idx] = None

        elif category == "Scroll":
            if item.effect_type == "max_hits":
                self.max_hits += item.value
                self.hits += item.value
                msg = f"{item.name} used! MAX HP +{item.value}!"
            elif item.effect_type == "agility":
                self.agility += item.value
                msg = f"{item.name} used! Agility +{item.value}!"
            elif item.effect_type == "strength":
                self.str += item.value
                msg = f"{item.name} used! Strength +{item.value}!"

            self.game.stats["scrolls_read"] += 1
            self.inventory.category_items[category][slot_idx] = None

        elif category == "Potion":
            effect_duration = item.effect_duration * 60
            self.add_potion_effect(item.effect_type, item.value, effect_duration)
            msg = f"{item.name} used! {item.effect_type} +{item.value} for {item.effect_duration} min!"

            self.game.stats["potions_drunk"] += 1
            self.inventory.category_items[category][slot_idx] = None

        return msg

    def drop_item(self, category: str, slot_idx: int) -> str:
        item = self.inventory.category_items[category][slot_idx]
        if item is None: return ""
        self.inventory.category_items[category][slot_idx] = None
        if category == "Weapon" and item == self.current_weapon:
            self.current_weapon = None
            self.update_stats()
        return f"Thrown away: {item.name}"

    def to_dict(self):
        return {
            "name": self.name,
            "position": [self.y, self.x],
            "hits": self.hits,
            "max_hits": self.max_hits,
            "str": self.str,
            "agility": self.agility,
            "gold": self.gold,
            "exp": self.exp,
            "exp_to_level_up": self.exp_to_level_up,
            "level": self.level,
            "inventory": self.inventory.to_dict(),
            "current_weapon": self.current_weapon.to_dict() if self.current_weapon else None,
            "potion_effects": self.potion_effects
        }