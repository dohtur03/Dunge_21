import random
from domain.enemy import *
from domain.item import Item
from domain.key_validator import check_level_passability  # Подключаем наш умный алгоритм!


class Room:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.is_start = False
        self.is_end = False

        self.enemies: list[Enemy] = []
        self.item_drops: dict[tuple[int, int], dict] = {}

    @property
    def center(self) -> tuple[int, int]:
        return (self.y + self.height // 2, self.x + self.width // 2)

    def intersects(self, other: 'Room') -> bool:
        return (self.x <= other.x + other.width and self.x + self.width >= other.x and
                self.y <= other.y + other.height and self.y + self.height >= other.y)


class Level:
    def __init__(self, stage: int, max_width: int, max_height: int, director=None):
        self.stage = stage
        self.max_width = max_width
        self.max_height = max_height
        self.director = director  # Сохраняем Режиссера

        self.rooms: list[Room] = []
        self.corridors: set[tuple[int, int]] = set()
        self.corridor_segments: list[set[tuple[int, int]]] = []
        self.doors: dict[tuple[int, int], str] = {}
        self.keys: dict[tuple[int, int], str] = {}
        self.enemies: list[Enemy] = []
        self.item_drops: dict[tuple[int, int], dict] = {}
        self.start_pos = (0, 0)
        self.player_start_pos = (0, 0)
        self.end_pos = (0, 0)

    def generate_level(self):
        while True:
            self.rooms.clear()
            self.corridors.clear()
            self.corridor_segments.clear()
            self.doors.clear()
            self.keys.clear()
            self.enemies.clear()
            self.item_drops.clear()

            start_y_offset = 6
            section_w = self.max_width // 3
            section_h = (self.max_height - start_y_offset) // 3
            min_room_w, min_room_h = 5, 4

            for row in range(3):
                for col in range(3):
                    sec_x1 = col * section_w + 1
                    sec_y1 = row * section_h + start_y_offset
                    sec_x2 = sec_x1 + section_w - 2
                    sec_y2 = sec_y1 + section_h - 2

                    room_w = random.randint(min_room_w, max(min_room_w, section_w - 4))
                    room_h = random.randint(min_room_h, max(min_room_h, section_h - 4))
                    room_x = random.randint(sec_x1, max(sec_x1, sec_x2 - room_w))
                    room_y = random.randint(sec_y1, max(sec_y1, sec_y2 - room_h))

                    new_room = Room(room_x, room_y, room_w, room_h)
                    self.rooms.append(new_room)

            start_room, exit_room = self._assign_start_and_exit()
            self.start_pos = start_room.center

            # 3. Строим коридоры
            for row in range(3):
                for col in range(3):
                    current_idx = row * 3 + col
                    if col < 2:
                        right_idx = row * 3 + (col + 1)
                        self._create_corridor(self.rooms[current_idx], self.rooms[right_idx])
                    if row < 2:
                        bottom_idx = (row + 1) * 3 + col
                        self._create_corridor(self.rooms[current_idx], self.rooms[bottom_idx])

            # 4. Расставляем двери и ключи
            self._place_doors_and_keys()

            # 5. Собираем все проходимые клетки для валидатора
            walkable_cells = set(self.corridors)
            for r in self.rooms:
                for y in range(r.y, r.y + r.height):
                    for x in range(r.x, r.x + r.width):
                        walkable_cells.add((y, x))

            # 6. Запускаем умную проверку на софтлок!
            is_valid = check_level_passability(
                start_pos=self.player_start_pos,
                exit_pos=self.end_pos,
                walkable_cells=walkable_cells,
                keys=self.keys,
                doors=self.doors
            )

            # Если лабиринт проходим - выходим из цикла! Иначе всё начнется заново.
            if is_valid:
                break

        # Спавним врагов и лут только после того, как убедились, что уровень идеален
        self._spawn_entities()

    def _place_doors_and_keys(self):
        # Заменили Green на Yellow по твоей просьбе!
        colors = ["Red", "Blue", "Yellow"]
        num_doors = random.randint(1, 3)
        chosen_colors = random.sample(colors, num_doors)

        # Функция, проверяющая, лежит ли клетка ровно на стене комнаты (это дверной проем)
        def is_wall(cy, cx):
            for r in self.rooms:
                if (cy == r.y - 1 or cy == r.y + r.height) and (r.x - 1 <= cx <= r.x + r.width):
                    return True
                if (cx == r.x - 1 or cx == r.x + r.width) and (r.y - 1 <= cy <= r.y + r.height):
                    return True
            return False

        available_segments = self.corridor_segments.copy()
        random.shuffle(available_segments)

        for color in chosen_colors:
            if not available_segments:
                break
            segment = available_segments.pop()

            # Находим оба входа в этот коридор
            doorways = [cell for cell in segment if is_wall(cell[0], cell[1])]
            if not doorways:
                doorways = [random.choice(list(segment))]

            # Ставим цветные двери на ОБА входа (те самые "2 двери")
            for dy, dx in doorways:
                self.doors[(dy, dx)] = color

        # Прячем ключи
        for color in chosen_colors:
            while True:
                r = random.choice(self.rooms)
                ky = random.randint(r.y, r.y + r.height - 1)
                kx = random.randint(r.x, r.x + r.width - 1)

                if (ky, kx) not in self.keys and (ky, kx) != self.end_pos and (ky, kx) != self.player_start_pos:
                    self.keys[(ky, kx)] = color
                    break

    def _create_corridor(self, room1: Room, room2: Room):
        corridor_cells = set()  # Собираем отдельный коридор
        y1, x1 = room1.center
        y2, x2 = room2.center
        if random.choice([True, False]):
            for x in range(min(x1, x2), max(x1, x2) + 1):
                corridor_cells.add((y1, x))
                self.corridors.add((y1, x))
            for y in range(min(y1, y2), max(y1, y2) + 1):
                corridor_cells.add((y, x2))
                self.corridors.add((y, x2))
        else:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                corridor_cells.add((y, x1))
                self.corridors.add((y, x1))
            for x in range(min(x1, x2), max(x1, x2) + 1):
                corridor_cells.add((y2, x))
                self.corridors.add((y2, x))

        self.corridor_segments.append(corridor_cells)

    def _assign_start_and_exit(self):
        if len(self.rooms) < 2:
            start_room = self.rooms[0]
            exit_room = self.rooms[0]
        else:
            start_room, exit_room = random.sample(self.rooms, 2)

        for room in self.rooms:
            room.is_start = (room == start_room)

        self.player_start_pos = (
            random.randint(start_room.y, start_room.y + start_room.height - 1),
            random.randint(start_room.x, start_room.x + start_room.width - 1)
        )

        self.end_pos = (
            random.randint(exit_room.y, exit_room.y + exit_room.height - 1),
            random.randint(exit_room.x, exit_room.x + exit_room.width - 1)
        )

        return start_room, exit_room

    def _spawn_entities(self):
        available_classes = [Zombie, Ghost, Vampire, SnakeMage, Ogre, Mimic]

        food_to_spawn = self.director.get_guaranteed_health_drops() if self.director else 0

        for room in self.rooms:
            if room.is_start: continue

            min_enemies = 0
            if self.stage >= 10: min_enemies = 1
            if self.stage >= 18: min_enemies = 2
            max_enemies = min(5, 1 + (self.stage // 4))

            if self.director:
                modifier = self.director.get_enemy_count_modifier()
                max_enemies = max(1, int(max_enemies * modifier))
                min_enemies = int(min_enemies * modifier)

            num_enemies = random.randint(min_enemies, max_enemies)

            stat_buff = self.director.get_enemy_stats_buff() if self.director else 0

            for _ in range(num_enemies):
                ey = random.randint(room.y, room.y + room.height - 1)
                ex = random.randint(room.x, room.x + room.width - 1)

                if (ey, ex) != self.end_pos and (ey, ex) not in self.keys:
                    EnemyClass = random.choice(available_classes)
                    enemy = EnemyClass(ey, ex, room, self.stage, self.director)

                    extra_hp = (self.stage - 1) * 3 + (stat_buff * 5)
                    enemy.max_hp = max(1, enemy.max_hp + extra_hp)
                    enemy.hp = enemy.max_hp

                    extra_str = (self.stage // 5) + stat_buff
                    enemy.strength = max(1, enemy.strength + extra_str)

                    self.enemies.append(enemy)

            item_chance = self.director.get_item_spawn_chance() if self.director else 0.4
            force_food = False

            if food_to_spawn > 0 and random.random() < 0.6:
                item_chance = 1.0
                force_food = True

            if random.random() < item_chance:
                iy = random.randint(room.y, room.y + room.height - 1)
                ix = random.randint(room.x, room.x + room.width - 1)

                if (iy, ix) != self.end_pos and (iy, ix) not in self.item_drops and (iy, ix) not in self.keys:
                    category = "Food" if force_food else random.choice(list(Item.items.keys()))

                    if force_food:
                        food_to_spawn -= 1

                    item_data = random.choice(Item.items[category])

                    item = Item(
                        name=item_data["name"],
                        effect_duration=item_data["effect_duration"],
                        effect_type=item_data["effect_type"],
                        value=item_data["value"],
                        description_template=item_data["description_template"]
                    )

                    self.item_drops[(iy, ix)] = {
                        "category": category,
                        "item": item
                    }