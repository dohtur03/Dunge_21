import random
from domain.enemy import Enemy

class Room:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.is_start = False
        self.is_end = False

        self.enemies = []
        self.items = []

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

        # Коллекции для хранения объектов на карте
        self.enemies: list[Enemy] = []
        self.gold_drops: dict[tuple[int, int], int] = {}  # Словарь: координаты (y, x) -> количество золота

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

        self.rooms[0].is_start = True
        self.rooms[-1].is_end = True
        self.start_pos = self.rooms[0].center
        self.end_pos = self.rooms[-1].center

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

    def _spawn_entities(self):
        """Раскидывает монстров и золото по комнатам"""
        enemy_templates = [
            {"name": "Goblin", "char": "g", "hp": 5, "strength": 2, "exp": 10},
            {"name": "Skeleton", "char": "s", "hp": 8, "strength": 3, "exp": 15},
            {"name": "Orc", "char": "O", "hp": 15, "strength": 5, "exp": 30}
        ]

        for room in self.rooms:
            # В стартовой комнате всегда безопасно
            if room.is_start:
                continue

            # Спавним от 0 до 2 врагов в комнате
            for _ in range(random.randint(0, 2)):
                ey = random.randint(room.y, room.y + room.height - 1)
                ex = random.randint(room.x, room.x + room.width - 1)

                # Исключаем спавн прямо на выходе
                if (ey, ex) != self.end_pos:
                    template = random.choice(enemy_templates)
                    enemy = Enemy(template["name"], template["char"], ey, ex,
                                  template["hp"], template["strength"], template["exp"])
                    self.enemies.append(enemy)

            # Спавним от 0 до 2 кучек золота
            for _ in range(random.randint(0, 2)):
                gy = random.randint(room.y, room.y + room.height - 1)
                gx = random.randint(room.x, room.x + room.width - 1)

                if (gy, gx) != self.end_pos:
                    self.gold_drops[(gy, gx)] = random.randint(10, 50)