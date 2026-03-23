import random

class Enemy:
    def __init__(self, y: int, x: int, room):
        self.y = y
        self.x = x
        self.room = room
        self.name = "Unknown"
        self.char = "?"
        self.color_pair = 7
        self.hp = 10
        self.max_hp = 10
        self.strength = 1
        self.agility = 1
        self.hostility = 5
        self.exp_reward = 10
        self.is_engaged = False  # Заметил ли враг игрока

    def take_damage(self, damage: int) -> bool:
        """Возвращает True (удар прошел) или False (уворот/блок)"""
        self.hp -= damage
        self.is_engaged = True
        return True

    def attack(self, player) -> str:
        """Наносит урон, возвращает строку с описанием спецэффекта"""
        player.hits -= self.strength
        return ""

    def act(self, game):
        """Базовый ИИ: проверить дистанцию, ударить или сделать шаг"""
        dist = abs(self.y - game.player.y) + abs(self.x - game.player.x)
        if dist == 1:
            msg = self.attack(game.player)
            if msg: game.action_msg = msg
        elif dist <= self.hostility or self.is_engaged:
            self.is_engaged = True
            self._move_towards(game)

    def _move_towards(self, game):
        """Простой алгоритм поиска пути к игроку"""
        dy = 1 if game.player.y > self.y else (-1 if game.player.y < self.y else 0)
        dx = 1 if game.player.x > self.x else (-1 if game.player.x < self.x else 0)

        moves = [(self.y + dy, self.x + dx), (self.y + dy, self.x), (self.y, self.x + dx)]
        for ny, nx in moves:
            if game.can_move(ny, nx) and not self._is_occupied(ny, nx, game):
                self.y, self.x = ny, nx
                return

    def _is_occupied(self, y, x, game):
        if game.player.y == y and game.player.x == x: return True
        for e in game.current_level.enemies:
            if e.y == y and e.x == x: return True
        return False

    def is_visible(self):
        return True


class Zombie(Enemy):
    def __init__(self, y, x, room):
        super().__init__(y, x, room)
        self.name = "Zombie"
        self.char = "z"
        self.color_pair = 2  # Зеленый
        self.hp = 25
        self.strength = 3
        self.agility = 1
        self.hostility = 5
        self.exp_reward = 15


class Vampire(Enemy):
    def __init__(self, y, x, room):
        super().__init__(y, x, room)
        self.name = "Vampire"
        self.char = "v"
        self.color_pair = 1  # Красный
        self.hp = 25
        self.strength = 4
        self.agility = 8
        self.hostility = 8
        self.exp_reward = 35
        self.first_hit_taken = False

    def take_damage(self, damage: int):
        self.is_engaged = True
        if not self.first_hit_taken:
            self.first_hit_taken = True
            return False  # Уворот от первой атаки!
        self.hp -= damage
        return True

    def attack(self, player):
        super().attack(player)
        player.max_hits = max(1, player.max_hits - 1)  # Крадет Макс ХП
        if player.hits > player.max_hits: player.hits = player.max_hits
        return "Vampire drained your MAX HP!"


class Ghost(Enemy):
    def __init__(self, y, x, room):
        super().__init__(y, x, room)
        self.name = "Ghost"
        self.char = "g"
        self.color_pair = 7  # Белый
        self.hp = 8
        self.strength = 2
        self.agility = 9
        self.hostility = 3
        self.exp_reward = 20

        # Новые переменные для плавного исчезновения
        self._is_faded = False
        self._turn_counter = 0

    def is_visible(self):
        if self.is_engaged:
            return True
        # Теперь возвращаем конкретное состояние, а не рандом
        return not self._is_faded

    def act(self, game):
        if self.is_engaged:
            super().act(game)
        else:
            # Считаем ходы. Каждые 4 хода призрак меняет видимость
            self._turn_counter += 1
            if self._turn_counter >= 4:
                self._is_faded = not self._is_faded
                self._turn_counter = 0

            # Телепортация (шанс 5%, чтобы не летал по комнате каждую секунду)
            if random.random() < 0.05:
                self.y = random.randint(self.room.y, self.room.y + self.room.height - 1)
                self.x = random.randint(self.room.x, self.room.x + self.room.width - 1)

class Ogre(Enemy):
    def __init__(self, y, x, room):
        super().__init__(y, x, room)
        self.name = "Ogre"
        self.char = "O"
        self.color_pair = 4  # Желтый
        self.hp = 40
        self.strength = 12
        self.agility = 1
        self.hostility = 5
        self.exp_reward = 50
        self.resting = False

    def act(self, game):
        if self.resting:
            self.resting = False
            return  # Пропускает ход

        for _ in range(2):  # Ходит на 2 клетки
            dist = abs(self.y - game.player.y) + abs(self.x - game.player.x)
            if dist == 1:
                msg = self.attack(game.player)
                if msg: game.action_msg = msg
                self.resting = True  # Отдыхает после удара
                break
            else:
                self._move_towards(game)


class SnakeMage(Enemy):
    def __init__(self, y, x, room):
        super().__init__(y, x, room)
        self.name = "Snake-Mage"
        self.char = "s"
        self.color_pair = 7  # Белый
        self.hp = 15
        self.strength = 3
        self.agility = 10
        self.hostility = 10
        self.exp_reward = 40
        self.diag_dir = random.choice([(1, 1), (1, -1), (-1, 1), (-1, -1)])

    def _move_towards(self, game):
        # Ходит только по диагонали
        dy, dx = self.diag_dir
        if game.can_move(self.y + dy, self.x + dx) and not self._is_occupied(self.y + dy, self.x + dx, game):
            self.y += dy;
            self.x += dx
        else:
            self.diag_dir = random.choice([(1, 1), (1, -1), (-1, 1), (-1, -1)])

    def attack(self, player):
        super().attack(player)
        if random.random() < 0.3:  # 30% шанс усыпить
            player.sleep_turns += 1
            return "Snake-Mage put you to SLEEP!"
        return ""