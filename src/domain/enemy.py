import random


class Enemy:
    def __init__(self, y: int, x: int, room, stage: int, director):
        self.y = y
        self.x = x
        self.room = room
        self.stage = stage

        # Получаем настройки сложности (теперь они влияют мягче)
        self.difficulty_buff = director.get_enemy_stats_buff()

        self.name = "Unknown"
        self.char = "?"
        self.color_pair = 7

        # МЯГКАЯ ФОРМУЛА HP: База 12 + всего 2 HP за каждый этаж
        self.hp = 12 + (stage * 2) + self.difficulty_buff
        self.max_hp = self.hp

        # УРОН: Растет медленно, только каждые 4 этажа
        self.strength = 2 + (stage // 4)
        self.agility = 1
        self.hostility = 5
        self.exp_reward = 10 + stage
        self.is_engaged = False

    def take_damage(self, damage: int) -> bool:
        self.hp -= damage
        self.is_engaged = True
        return True

    def attack(self, game) -> str:
        player = game.player
        # Шанс уворота (балансируем под игрока)
        dodge_chance = min(player.agility * 0.01, 0.50)

        if random.random() < dodge_chance:
            return f"Dodged! {self.name}'s attack missed."

        player.hits -= self.strength
        game.stats["hits_taken"] += 1
        return ""

    def act(self, game):
        dist = abs(self.y - game.player.y) + abs(self.x - game.player.x)
        if dist == 1:
            msg = self.attack(game)
            if msg: game.action_msg = msg
        elif dist <= self.hostility or self.is_engaged:
            self.is_engaged = True
            moved = self._move_towards(game)
            if not moved:
                self.wander(game)
        else:
            self.wander(game)

    def wander(self, game):
        dy, dx = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)])
        if game.can_move(self.y + dy, self.x + dx) and not self._is_occupied(self.y + dy, self.x + dx, game):
            self.y += dy
            self.x += dx

    def _move_towards(self, game) -> bool:
        dy = 1 if game.player.y > self.y else (-1 if game.player.y < self.y else 0)
        dx = 1 if game.player.x > self.x else (-1 if game.player.x < self.x else 0)
        moves = [(self.y + dy, self.x + dx), (self.y + dy, self.x), (self.y, self.x + dx)]
        for ny, nx in moves:
            if ny != self.y and nx != self.x: continue
            if game.can_move(ny, nx) and not self._is_occupied(ny, nx, game):
                self.y, self.x = ny, nx
                return True
        return False

    def _is_occupied(self, y, x, game):
        if game.player.y == y and game.player.x == x: return True
        for e in game.current_level.enemies:
            if e.y == y and e.x == x: return True
        return False

    def is_visible(self):
        return True


# --- МОНСТРЫ (Light Version) ---

class Zombie(Enemy):
    def __init__(self, y, x, room, stage, director):
        super().__init__(y, x, room, stage, director)
        self.name = "Zombie"
        self.char = "z"
        self.color_pair = 4
        # HP Зомби: 20 + 3 за уровень. На 10 этаже будет 50 HP.
        self.hp = 20 + (stage * 3) + self.difficulty_buff
        self.max_hp = self.hp
        self.strength = 3 + (stage // 5)


class Vampire(Enemy):
    def __init__(self, y, x, room, stage, director):
        super().__init__(y, x, room, stage, director)
        self.name = "Vampire"
        self.char = "v"
        self.color_pair = 1
        self.hp = 18 + (stage * 2)
        self.max_hp = self.hp
        self.strength = 3 + (stage // 3)
        self.first_hit_taken = False

    def take_damage(self, damage: int):
        self.is_engaged = True
        if not self.first_hit_taken:
            self.first_hit_taken = True
            return False
        self.hp -= damage
        return True


class Ogre(Enemy):
    def __init__(self, y, x, room, stage, director):
        super().__init__(y, x, room, stage, director)
        self.name = "Ogre"
        self.char = "O"
        self.color_pair = 2
        # Огр теперь не убивает с одного удара: 35 HP + 4 за уровень
        self.hp = 35 + (stage * 4) + (self.difficulty_buff * 2)
        self.max_hp = self.hp
        self.strength = 5 + (stage // 2)


class Ghost(Enemy):
    def __init__(self, y, x, room, stage, director):
        super().__init__(y, x, room, stage, director)
        self.name = "Ghost"
        self.char = "g"
        self.color_pair = 3
        self.hp = 8 + (stage * 2)
        self.max_hp = self.hp


class SnakeMage(Enemy):
    def __init__(self, y, x, room, stage, director):
        super().__init__(y, x, room, stage, director)
        self.name = "Snake-Mage"
        self.char = "s"
        self.color_pair = 3
        self.hp = 12 + (stage * 2)
        self.max_hp = self.hp


class Mimic(Enemy):
    def __init__(self, y, x, room, stage, director):
        super().__init__(y, x, room, stage, director)
        self.name = "Mimic"

        # 1. Маскировка (выбираем случайный вид предмета)
        # † - Оружие, ð - Зелье, § - Свиток, ♣ - Еда
        disguises = [("†", 3), ("ð", 1), ("§", 2), ("♣", 4)]
        chosen_char, chosen_color = random.choice(disguises)

        self.char = chosen_char
        self.color_pair = chosen_color
        self.is_disguised = True

        # 2. Сбалансированные статы (из твоего последнего запроса)
        self.hp = 25 + (stage * 3) + self.difficulty_buff
        self.max_hp = self.hp
        self.strength = 3 + (stage // 3)
        self.agility = 9
        self.hostility = 1  # Мимик не нападает первым, пока ты далеко
        self.exp_reward = 25 + stage

    def reveal(self):
        """Процесс разоблачения монстра"""
        if self.is_disguised:
            self.is_disguised = False
            self.char = "m"  # Настоящий облик мимика
            self.color_pair = 3  # Коричневый/желтый
            return "The item suddenly bites you! It's a Mimic!"
        return ""

    def take_damage(self, damage: int):
        # Если ударить замаскированного мимика, он раскроется
        msg = self.reveal()
        return super().take_damage(damage)

    def act(self, game):
        if self.is_disguised:
            dist = abs(self.y - game.player.y) + abs(self.x - game.player.x)
            if dist <= 1:
                reveal_msg = self.reveal()
                if reveal_msg:
                    game.action_msg = reveal_msg
                attack_msg = self.attack(game)
                if attack_msg:
                    game.action_msg = f"{reveal_msg} {attack_msg}"
            else:
                return
        else:
            super().act(game)