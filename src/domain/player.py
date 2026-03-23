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

        # Выдаем стартовые предметы
        for category_name in Item.items:
            for i in range(5):
                self.inventory.category_items[category_name][i] = Item(**random.choice(Item.items[category_name]))

    def update_stats(self):
        self.total_str = self.str + (self.current_weapon.value if self.current_weapon is not None else 0)

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

        if effect_type == "max_hits":
            self.max_hits += value
            self.hits += value
        elif effect_type == "strength":
            self.str += value
        elif effect_type == "agility":
            self.agility += value

    def update_effects(self):
        current_time = time.time()
        all_effects = self.potion_effects.copy()
        self.potion_effects = []

        max_hp_bonus = str_bonus = agi_bonus = 0

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

        self.max_hits -= max_hp_bonus
        self.hits -= max_hp_bonus

        if self.hits <= 0:
            self.hits = 1
        self.str -= str_bonus
        self.agility -= agi_bonus

    def use_item(self, category: str, slot_idx: int) -> str:
        item = self.inventory.category_items[category][slot_idx]
        if item is None: return ""

        msg = ""

        if category == "Weapon":
            if self.current_weapon is item:
                self.current_weapon = None
                msg = f"{item.name} unequipped"
            else:
                # Если уже есть надетое оружие - выбрасываем его!
                if self.current_weapon is not None:
                    old_weapon = self.current_weapon

                    # Ищем свободную соседнюю клетку для выброса
                    drop_y, drop_x = self.y, self.x
                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
                        ny, nx = self.y + dy, self.x + dx
                        # Проверяем, можно ли туда ходить и нет ли там уже другого предмета
                        if self.game.can_move(ny, nx) and (ny, nx) not in self.game.current_level.item_drops:
                            drop_y, drop_x = ny, nx
                            break

                    # Кладем старое оружие на пол уровня
                    self.game.current_level.item_drops[(drop_y, drop_x)] = {
                        "category": "Weapon",
                        "item": old_weapon
                    }

                    # Удаляем старое оружие из инвентаря
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
                msg = "HP full!"
            else:
                self.hits += item.value
                if self.hits >= self.max_hits:
                    msg = f"Eaten {item.name}! Restored {self.max_hits - old_hits} HP!"
                    self.hits = self.max_hits
                else:
                    msg = f"Eaten {item.name}! Restored {item.value} HP!"
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
            self.inventory.category_items[category][slot_idx] = None

        elif category == "Potion":
            effect_duration = item.effect_duration * 60
            self.add_potion_effect(item.effect_type, item.value, effect_duration)
            msg = f"{item.name} used! {item.effect_type} +{item.value} for {item.effect_duration} min!"
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