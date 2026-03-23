import time
from domain.level import Level
from domain.player import Player
from domain.inventory import Inventory
from domain.item import Item


class Game:
    def __init__(self, player_name: str):
        self.action_msg = ""
        self.start_time = time.time()
        self.player_score = 0
        self.player_stage = 1

        # Теперь Игрок — это отдельный независимый объект
        self.player = Player(player_name, self)

        self.generate_new_stage()

    def generate_new_stage(self):
        self.current_level = Level(self.player_stage, 75, 28)
        self.current_level.generate_level()
        self.player.y, self.player.x = self.current_level.start_pos

    def get_score(self):
        return self.player_score

    def can_move(self, target_y: int, target_x: int) -> bool:
        if (target_y, target_x) in self.current_level.corridors: return True
        for room in self.current_level.rooms:
            if room.x <= target_x < room.x + room.width and room.y <= target_y < room.y + room.height:
                return True
        return False

    def process_turn(self, key) -> str | None:
        self.player.update_effects()
        self.player_score = int(time.time() - self.start_time)
        self.action_msg = ""
        turn_taken = False

        if self.player.hits <= 0: return "died"

        # Если игрок спит, он пропускает ход, но враги ходят!
        if self.player.sleep_turns > 0:
            self.player.sleep_turns -= 1
            self.action_msg = "You are SLEEPING! Zzz..."
            self._process_enemies()
            if self.player.hits <= 0: return "died"
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

        enemy_hit = None
        for enemy in self.current_level.enemies:
            if enemy.y == new_y and enemy.x == new_x:
                enemy_hit = enemy
                break

        if enemy_hit is not None:
            hit_success = enemy_hit.take_damage(self.player.total_str)
            if hit_success:
                if enemy_hit.hp <= 0:
                    self.current_level.enemies.remove(enemy_hit)
                    self.player.exp += enemy_hit.exp_reward
                    self.player.check_level_up()
                    self.action_msg = f"You killed {enemy_hit.name}!"
                else:
                    self.action_msg = f"You hit {enemy_hit.name}!"
            else:
                self.action_msg = f"{enemy_hit.name} DODGED!"
            turn_taken = True

        elif self.can_move(new_y, new_x):
            if (self.player.y, self.player.x) != (new_y, new_x):
                self.player.y, self.player.x = new_y, new_x
                turn_taken = True

            pos = (self.player.y, self.player.x)
            if pos in self.current_level.gold_drops:
                self.player.gold += self.current_level.gold_drops[pos]
                del self.current_level.gold_drops[pos]

            if pos == self.current_level.end_pos:
                self.player_stage += 1
                self.generate_new_stage()
                return "stage_cleared"

                # Как только игрок сделал действие - ходят враги
        if turn_taken:
            self._process_enemies()

        if self.player.hits <= 0: return "died"
        return "continue"

    def _process_enemies(self):
        for enemy in self.current_level.enemies:
            if enemy.hp > 0:
                enemy.act(self)

    # Прокси-методы для инвентаря (чтобы не переписывать логику меню инвентаря)
    def use_item(self, category: str, slot_idx: int) -> str:
        return self.player.use_item(category, slot_idx)

    def drop_item(self, category: str, slot_idx: int) -> str:
        return self.player.drop_item(category, slot_idx)

    def save_game_data_to_dict(self) -> dict:
        return {
            "score": self.player_score,
            "stage": self.player_stage,
            "start_time": self.start_time,
            "player_data": self.player.to_dict()
        }

    @classmethod
    def from_dict(cls, data: dict):
        game = cls.__new__(cls)
        game.player_score = data.get("score", 0)
        game.player_stage = data.get("stage", 1)
        game.start_time = data.get("start_time", time.time())

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
            # Привязываем ссылку к инвентарю
            for i, item in enumerate(game.player.inventory.category_items["Weapon"]):
                if item and item.name == game.player.current_weapon.name:
                    game.player.inventory.category_items["Weapon"][i] = game.player.current_weapon
                    break

        game.player.update_stats()

        game.current_level = Level(game.player_stage, 75, 28)
        game.current_level.generate_level()

        return game