import random
from domain.level import Level
from domain.player import Player
from domain.inventory import Inventory
from domain.item import Item
from domain.director import GameDirector
from domain.fog import FogOfWar


class Game:
    def __init__(self, player_name: str):
        self.action_msg = ""
        self.player_stage = 1
        self.player = Player(player_name, self)
        self.director = GameDirector()  # Создаем Режиссера
        self.stats = {
            "treasures": 0,
            "level_reached": 1,
            "enemies_killed": 0,
            "food_eaten": 0,
            "elixirs_drunk": 0,
            "scrolls_read": 0,
            "hits_dealt": 0,
            "hits_taken": 0,
            "cells_walked": 0
        }
        self.collected_keys = set()
        self.fow = FogOfWar()
        self.generate_new_stage()

    def generate_new_stage(self):
        self.collected_keys.clear()
        self.current_level = Level(self.player_stage, 75, 28, self.director)
        self.current_level.generate_level()
        self.player.y, self.player.x = self.current_level.start_pos
        self.fow.reset()
        self.fow.update(self.player.y, self.player.x, self.current_level)

    def get_score(self):
        return self.player.gold

    def can_move(self, target_y: int, target_x: int, is_player: bool = False) -> bool:
        if not is_player and hasattr(self, 'current_level') and (target_y, target_x) in self.current_level.doors:
            return False

        if (target_y, target_x) in self.current_level.corridors:
            return True
        for room in self.current_level.rooms:
            if room.x <= target_x < room.x + room.width and room.y <= target_y < room.y + room.height:
                return True
        return False

    def process_turn(self, key) -> str | None:
        self.player.update_effects()
        self.action_msg = ""
        turn_taken = False

        if self.player.hits <= 0:
            return "died"

        if self.player.sleep_turns > 0:
            self.player.sleep_turns -= 1
            self.action_msg = "You are SLEEPING! Zzz..."
            self._process_enemies()
            if self.player.hits <= 0:
                return "died"
            return "continue"

        new_y, new_x = self.player.y, self.player.x

        if key in (119, 259):
            new_y -= 1
        elif key in (115, 258):
            new_y += 1
        elif key in (97, 260):
            new_x -= 1
        elif key in (100, 261):
            new_x += 1
        elif key == 105:
            return "open_inventory"
        elif key == 113:
            return "request_quit"
        elif key == 104:
            return "classic_inv_Weapon"
        elif key == 106:
            return "classic_inv_Food"
        elif key == 107:
            return "classic_inv_Potion"
        elif key == 101:
            return "classic_inv_Scroll"

        enemy_hit = None
        for enemy in self.current_level.enemies:
            if enemy.y == new_y and enemy.x == new_x:
                enemy_hit = enemy
                break

        if enemy_hit is not None:
            self.stats["hits_dealt"] += 1
            hit_success = enemy_hit.take_damage(self.player.total_str)
            if hit_success:
                if enemy_hit.hp <= 0:
                    self.current_level.enemies.remove(enemy_hit)
                    self.player.exp += enemy_hit.exp_reward
                    self.player.check_level_up()
                    gold_reward = random.randint(10, 30)
                    self.player.gold += gold_reward
                    self.action_msg = f"You killed {enemy_hit.name} and found {gold_reward} gold!"
                else:
                    self.action_msg = f"You hit {enemy_hit.name}!"
            else:
                self.action_msg = f"{enemy_hit.name} DODGED!"
            turn_taken = True

        elif self.can_move(new_y, new_x, is_player=True):
            if (new_y, new_x) in self.current_level.doors:
                req_color = self.current_level.doors[(new_y, new_x)]
                if req_color in self.collected_keys:
                    del self.current_level.doors[(new_y, new_x)]
                    self.action_msg = f"Unlocked the {req_color} door!"
                else:
                    self.action_msg = f"The door is locked. You need the {req_color} key!"
                    new_y, new_x = self.player.y, self.player.x
                    turn_taken = False

            if (self.player.y, self.player.x) != (new_y, new_x):
                self.player.y, self.player.x = new_y, new_x
                turn_taken = True
                self.stats["cells_walked"] += 1

            pos = (self.player.y, self.player.x)

            if pos in self.current_level.keys:
                key_color = self.current_level.keys[pos]
                self.collected_keys.add(key_color)
                del self.current_level.keys[pos]
                self.action_msg = f"Picked up the {key_color} key!"

            elif pos in self.current_level.item_drops:
                drop_info = self.current_level.item_drops[pos]
                category = drop_info["category"]
                item = drop_info["item"]

                item_added = False
                for i in range(9):
                    if self.player.inventory.category_items[category][i] is None:
                        self.player.inventory.category_items[category][i] = item
                        del self.current_level.item_drops[pos]
                        self.action_msg = f"Picked up: {item.name}!"
                        item_added = True
                        break

                if not item_added:
                    self.action_msg = f"Inventory full! Can't pick up {item.name}."

            if pos == self.current_level.end_pos:
                self.player_stage += 1
                if self.player_stage > 21:
                    return "win"

                # --- БАЛАНС: Оцениваем успехи перед новым уровнем! ---
                self.director.evaluate_performance(self.player)

                self.generate_new_stage()
                return "stage_cleared"

        if turn_taken:
            self.director.record_turn()  # Считаем ходы
            hp_before = self.player.hits  # Запоминаем ХП до атак мобов

            self._process_enemies()

            # Если ХП убавилось, докладываем Режиссеру об уроне
            if self.player.hits < hp_before:
                self.director.record_damage_taken(hp_before - self.player.hits)

        if self.player.hits <= 0:
            return "died"

        self.fow.update(self.player.y, self.player.x, self.current_level)
        return "continue"

    def _process_enemies(self):
        for enemy in self.current_level.enemies:
            if enemy.hp > 0:
                enemy.act(self)

    def use_item(self, category: str, slot_idx: int) -> str:
        return self.player.use_item(category, slot_idx)

    def drop_item(self, category: str, slot_idx: int) -> str:
        return self.player.drop_item(category, slot_idx)

    def save_game_data_to_dict(self) -> dict:
        self.stats["treasures"] = self.player.gold
        self.stats["level_reached"] = self.player_stage

        return {
            "stats": self.stats,
            "stage": self.player_stage,
            "collected_keys": list(self.collected_keys),
            "difficulty": self.director.difficulty_multiplier,
            "explored_cells": [list(cell) for cell in self.fow.explored_cells],
            "player_data": self.player.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict):
        game = cls.__new__(cls)
        game.player_stage = data.get("stage", 1)
        game.collected_keys = set(data.get("collected_keys", []))
        game.director = GameDirector()
        game.director.difficulty_multiplier = data.get("difficulty", 1.0)

        game.stats = data.get("stats", {
            "treasures": 0, "level_reached": 1, "enemies_killed": 0,
            "food_eaten": 0, "elixirs_drunk": 0, "scrolls_read": 0,
            "hits_dealt": 0, "hits_taken": 0, "cells_walked": 0
        })

        p_data = data.get("player_data", data)
        p_name = p_data.get("name", p_data.get("player_name", "Hero"))
        game.player = Player(p_name, game)
        game.player.y, game.player.x = p_data.get("position", [0, 0])
        game.player.hits = p_data.get("hits", p_data.get("player_hits", 10))
        game.player.max_hits = p_data.get("max_hits", p_data.get("player_max_hits", 20))
        game.player.str = p_data.get("str", p_data.get("player_str", 10))
        game.player.agility = p_data.get("agility", p_data.get("player_agility", 10))
        game.player.gold = p_data.get("gold", p_data.get("player_gold", 0))
        game.player.exp = p_data.get("exp", p_data.get("player_exp", 0))

        exp_to_level = p_data.get("exp_to_level_up", p_data.get("player_exp_to_level_up", 50))
        game.player.exp_to_level_up = 50 if exp_to_level == "?" else exp_to_level
        game.player.level = p_data.get("level", p_data.get("player_level", 1))
        game.player.potion_effects = p_data.get("potion_effects", [])

        inv_data = p_data.get("inventory", {})
        game.player.inventory = Inventory.from_dict(p_name, game, inv_data)

        weapon_data = p_data.get("current_weapon")
        if weapon_data:
            game.player.current_weapon = Item.from_dict(weapon_data)
            for i, item in enumerate(game.player.inventory.category_items["Weapon"]):
                if item and item.name == game.player.current_weapon.name:
                    game.player.inventory.category_items["Weapon"][i] = game.player.current_weapon
                    break

        game.player.update_stats()
        game.current_level = Level(game.player_stage, 75, 28, game.director)
        game.current_level.generate_level()

        game.fow = FogOfWar()

        explored_data = data.get("explored_cells", [])
        game.fow.explored_cells = {tuple(cell) for cell in explored_data}
        game.fow.update(game.player.y, game.player.x, game.current_level)

        return game

    def unequip_weapon(self) -> str:
        if self.player.current_weapon:
            msg = f"You put away your {self.player.current_weapon.name}."
            self.player.current_weapon = None
            self.player.update_stats()
            return msg
        return "Your hands are already empty."