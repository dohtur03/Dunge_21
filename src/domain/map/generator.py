import random

from domain.map.room import Room
from domain.map.corridor import Corridor
from domain.map.level import Level
from domain.map.config import LevelConfig


class LevelGenerator:
    def __init__(self, config: LevelConfig):
        self.config = config

    def generate(self) -> Level:
        rooms = self._place_rooms()
        connections = self._get_connections(rooms)

        corridors: list[Corridor] = []
        for first_room, second_room in connections:
            corridor = Corridor.between(first_room, second_room)
            if corridor.points:
                corridors.append(corridor)

        level = Level(
            width=self.config.map_width,
            height=self.config.map_height,
            rooms=rooms,
            connections=connections,
            corridors=corridors,
        )

        return level

    def _place_rooms(self) -> list[Room]:
        rooms = []
        config = self.config

        cell_width = config.map_width // config.rooms_in_column
        cell_height = config.map_height // config.rooms_in_row

        for row in range(config.rooms_in_row):
            for col in range(config.rooms_in_column):
                cell_left = col * cell_width
                cell_top = row * cell_height

                room_width = random.randint(
                    config.min_room_width,
                    min(config.max_room_width, cell_width - 2)
                )
                room_height = random.randint(
                    config.min_room_height,
                    min(config.max_room_height, cell_height - 2)
                )

                max_left = cell_left + cell_width - room_width - 1
                max_top = cell_top + cell_height - room_height - 1

                left = random.randint(cell_left + 1, max_left)
                top = random.randint(cell_top + 1, max_top)

                rooms.append(Room(left, top, room_width, room_height))

        return rooms

    def _get_connections(self, rooms: list[Room]) -> list[tuple[Room, Room]]:
        rows = self.config.rooms_in_row
        cols = self.config.rooms_in_column

        # 1. Собираем все возможные соседние пары по индексам
        # индексация: index = row * cols + col
        candidate_edges: list[tuple[int, int]] = []

        # горизонтальные соседи
        for row in range(rows):
            for col in range(cols - 1):
                left = row * cols + col
                right = row * cols + (col + 1)
                candidate_edges.append((left, right))

        # вертикальные соседи
        for row in range(rows - 1):
            for col in range(cols):
                top = row * cols + col
                bottom = (row + 1) * cols + col
                candidate_edges.append((top, bottom))

        # 2. Перемешиваем рёбра для рандома
        random.shuffle(candidate_edges)

        # 3. Строим случайное остовное дерево (random spanning tree) через union–find
        parent = list(range(len(rooms)))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra = find(a)
            rb = find(b)
            if ra != rb:
                parent[rb] = ra

        chosen_edges_idx: list[tuple[int, int]] = []

        for i, j in candidate_edges:
            if find(i) != find(j):
                union(i, j)
                chosen_edges_idx.append((i, j))

        # На этом этапе у нас уже связный граф (дерево),
        # каждая комната связана хотя бы с чем-то.

        # 4. (Опционально) добавим немного дополнительных рёбер для разнообразия
        extra_prob = 0.3  # 30% шанс добавить лишнюю связь

        used = set(tuple(sorted(e)) for e in chosen_edges_idx)

        for i, j in candidate_edges:
            key = tuple(sorted((i, j)))
            if key in used:
                continue
            if random.random() < extra_prob:
                chosen_edges_idx.append((i, j))
                used.add(key)

        # 5. Преобразуем индексы в реальные комнаты
        connections: list[tuple[Room, Room]] = [
            (rooms[i], rooms[j]) for i, j in chosen_edges_idx
        ]

        return connections