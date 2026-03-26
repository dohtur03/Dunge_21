import random
from domain.enemy import *
from domain.item import Item

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
    def __init__(self, stage: int, max_width: int, max_height: int):
        self.stage = stage
        self.max_width = max_width
        self.max_height = max_height

        self.rooms: list[Room] = []
        self.corridors: set[tuple[int, int]] = set()

        self.enemies: list[Enemy] = []

        self.item_drops: dict[tuple[int, int], dict] = {}

        self.start_pos = (0, 0)
        self.end_pos = (0, 0)

    def generate_level(self):
        # Жесткий отступ сверху. Теперь генерация комнат начнется минимум с Y=6.
        # Это даст огромный запас места для верхней стены и текста.
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
        self.end_pos = exit_room.center

        for row in range(3):
            for col in range(3):
                current_idx = row * 3 + col
                if col < 2:
                    right_idx = row * 3 + (col + 1)
                    self._create_corridor(self.rooms[current_idx], self.rooms[right_idx])
                if row < 2:
                    bottom_idx = (row + 1) * 3 + col
                    self._create_corridor(self.rooms[current_idx], self.rooms[bottom_idx])

        self._spawn_entities()

    def _create_corridor(self, room1: Room, room2: Room):
        """Строит Г-образный коридор из координат между центрами двух комнат"""
        y1, x1 = room1.center
        y2, x2 = room2.center

        # Случайным образом выбираем, как пойдет изгиб: сначала по горизонтали или по вертикали
        if random.choice([True, False]):
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self.corridors.add((y1, x))
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.corridors.add((y, x2))
        else:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.corridors.add((y, x1))
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self.corridors.add((y2, x))

    def _assign_start_and_exit(self):
        """Случайно выбирает комнаты для входа и выхода из уровня"""
        if len(self.rooms) < 2:
            # Техническая страховка: если комната одна, она и старт, и финиш
            start_room = self.rooms[0]
            exit_room = self.rooms[0]
        else:
            # 1. Выбираем 2 абсолютно разные комнаты из списка
            start_room, exit_room = random.sample(self.rooms, 2)

        # 2. Обновляем статус всех комнат
        for room in self.rooms:
            room.is_start = (room == start_room)

        # 3. Находим случайную свободную точку в стартовой комнате для игрока
        self.player_start_pos = (
            random.randint(start_room.y, start_room.y + start_room.height - 1),
            random.randint(start_room.x, start_room.x + start_room.width - 1)
        )

        # 4. Находим случайную точку в финишной комнате для выхода (>)
        # Если комнаты разные, выход никогда не окажется под игроком
        self.end_pos = (
            random.randint(exit_room.y, exit_room.y + exit_room.height - 1),
            random.randint(exit_room.x, exit_room.x + exit_room.width - 1)
        )

        return  start_room, exit_room
    def _spawn_entities(self):
        available_classes = [Zombie, Ghost, Vampire, SnakeMage, Ogre, Mimic]

        for room in self.rooms:
            if room.is_start: continue

            # 2. Прогрессия количества (Толпы растут с каждым этажом)
            min_enemies = 0
            if self.stage >= 10: min_enemies = 1
            if self.stage >= 18: min_enemies = 2

            # 1-й ур: макс 1 враг. 4-й ур: макс 2. 16+ ур: макс 5.
            max_enemies = min(5, 1 + (self.stage // 4))

            num_enemies = random.randint(min_enemies, max_enemies)

            # 3. Спавним вычисленное количество
            for _ in range(num_enemies):
                ey = random.randint(room.y, room.y + room.height - 1)
                ex = random.randint(room.x, room.x + room.width - 1)

                if (ey, ex) != self.end_pos:
                    EnemyClass = random.choice(available_classes)
                    enemy = EnemyClass(ey, ex, room)

                    # 4. Бафф статов (Прогрессия сложности)
                    # Враги становятся жирнее и бьют больнее на глубоких этажах
                    extra_hp = (self.stage - 1) * 3
                    enemy.max_hp += extra_hp
                    enemy.hp += extra_hp

                    extra_str = self.stage // 5
                    enemy.strength += extra_str

                    self.enemies.append(enemy)
            # 4. Спавн предметов (остается классическим)
            if random.random() < 0.4:
                iy = random.randint(room.y, room.y + room.height - 1)
                ix = random.randint(room.x, room.x + room.width - 1)

                if (iy, ix) != self.end_pos and (iy, ix) not in self.item_drops:
                    category = random.choice(list(Item.items.keys()))
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