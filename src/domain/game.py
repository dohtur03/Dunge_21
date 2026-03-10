import time
import random
from domain.inventory import Inventory
from domain.item import Item
from domain.level import Level


class Game:
    def __init__(self, player_name: str):
        self.player_name = player_name
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

        self.inventory = Inventory(player_name, self)

        # Заполняем инвентарь стартовыми предметами
        for category_name in Item.items:
            for i in range(5):
                self.inventory.category_items[category_name][i] = Item(**random.choice(Item.items[category_name]))

        # Генерируем первый уровень (логический размер 70x20)
        self.generate_new_stage()

    def generate_new_stage(self):
        """Создает новый уровень и помещает игрока на старт"""
        self.current_level = Level(self.player_stage, 70, 30)
        self.current_level.generate_level()

        # Ставим игрока в центр стартовой комнаты
        self.player_y, self.player_x = self.current_level.start_pos

    def get_score(self):
        return self.player_score

    def can_move(self, target_y: int, target_x: int) -> bool:
        """Проверяет, является ли клетка полом комнаты или коридором"""
        # 1. Проверяем коридоры
        if (target_y, target_x) in self.current_level.corridors:
            return True

        # 2. Проверяем комнаты
        for room in self.current_level.rooms:
            # Находится ли координата внутри границ комнаты
            if room.x <= target_x < room.x + room.width and room.y <= target_y < room.y + room.height:
                return True

        return False

    def process_turn(self, key) -> str | None:
        """Обработка одного хода/нажатия клавиши. Возвращает статус (например, 'quit') или None"""
        self.update_effects()
        self.player_score = int(time.time() - self.start_time)

        if self.player_hits <= 0:
            return "died"
        elif self.player_hits >= self.player_max_hits:
            self.player_hits = self.player_max_hits

        new_y, new_x = self.player_y, self.player_x

        if key == 119 or key == 259:  # w / UP
            new_y -= 1
        elif key == 115 or key == 258:  # s / DOWN
            new_y += 1
        elif key == 97 or key == 260:  # a / LEFT
            new_x -= 1
        elif key == 100 or key == 261:  # d / RIGHT
            new_x += 1
        elif key == 105:  # i
            return "open_inventory"
        elif key == 113:  # q
            return "request_quit"

        # Пробуем сделать шаг
        if self.can_move(new_y, new_x):
            self.player_y, self.player_x = new_y, new_x

            # Если дошли до выхода - переходим на следующий этап
            if (self.player_y, self.player_x) == self.current_level.end_pos:
                self.player_stage += 1
                self.generate_new_stage()
                return "stage_cleared"

        return "continue"

    def use_item(self, category: str, slot_idx: int) -> str:
        """Применяет эффект предмета и возвращает текст для всплывающего окна"""
        item = self.inventory.category_items[category][slot_idx]
        if item is None:
            return ""

        msg = ""
        if category == "Weapon":
            if self.current_weapon is item:
                self.current_weapon = None
                msg = f"{item.name} unequipped"
            else:
                self.current_weapon = item
                msg = f"{item.name} equipped"
            self.update_stats()

        elif category == "Food":
            old_hits = self.player_hits
            if old_hits == self.player_max_hits:
                msg = "HP full!"
            else:
                self.player_hits += item.value
                if self.player_hits >= self.player_max_hits:
                    msg = f"Eaten {item.name}! Restored {self.player_max_hits - old_hits} HP!"
                    self.player_hits = self.player_max_hits
                else:
                    msg = f"Eaten {item.name}! Restored {item.value} HP!"
            self.inventory.category_items[category][slot_idx] = None

        elif category == "Scroll":
            if item.effect_type == "max_hits":
                self.player_max_hits += item.value
                self.player_hits += item.value
                msg = f"{item.name} is used! MAX HP and current HP increased by {item.value}!"
            elif item.effect_type == "agility":
                self.player_agility += item.value
                msg = f"{item.name} is used! Agility increased by {item.value}!"
            elif item.effect_type == "strength":
                self.player_str += item.value
                msg = f"{item.name} is used! Strength increased by {item.value}!"
            self.inventory.category_items[category][slot_idx] = None

        elif category == "Potion":
            effect_duration = item.effect_duration * 60
            if item.effect_type == "max_hits":
                self.add_potion_effect("max_hits", item.value, effect_duration)
                msg = f"{item.name} is used! MAX HP +{item.value} for {item.effect_duration} min!"
            elif item.effect_type == "agility":
                self.add_potion_effect("agility", item.value, effect_duration)
                msg = f"{item.name} is used! Agility increased by {item.value} for {item.effect_duration} min!"
            elif item.effect_type == "strength":
                self.add_potion_effect("strength", item.value, effect_duration)
                msg = f"{item.name} is used! Strength increased by {item.value} for {item.effect_duration} min!"
            self.inventory.category_items[category][slot_idx] = None

        return msg

    def drop_item(self, category: str, slot_idx: int) -> str:
        """Выбрасывает предмет из инвентаря"""
        item = self.inventory.category_items[category][slot_idx]
        if item is None:
            return ""
        self.inventory.category_items[category][slot_idx] = None
        if category == "Weapon" and item == self.current_weapon:
            self.current_weapon = None
            self.update_stats()
        return f"Thrown away: {item.name}"

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
        game.inventory = Inventory.from_dict(game.player_name, game, inv_data)

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

        # Перегенерируем уровень для текущей стадии при загрузке игры
        game.current_level = Level(game.player_stage, 70, 30)
        game.current_level.generate_level()

        return game