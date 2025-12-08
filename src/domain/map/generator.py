import random
from typing import Sequence

from domain.map.room import Room
from domain.map.level import Level
from domain.map.config import LevelConfig
from domain.map.tile_factory import TileFactory


class LevelGenerator:
    def __init__(self, config: LevelConfig):
        self.config = config

    def generate(self) -> Level:
        rooms = self._place_rooms()
        connections = self._build_connections(rooms)

        level =  Level(
            width=self.config.map_width,
            height=self.config.map_height,
            rooms=rooms,
            connections=connections
        )

        for room in level.rooms:
            self._carve_room(room, level.tiles)
        for room_a, room_b in level.connections:
            self._carve_corridor(room_a, room_b, level.tiles)
        return level

    def _create_random_room(self) -> Room:
        config = self.config
        width = random.randint(config.min_room_width, config.max_room_width)
        height = random.randint(config.min_room_height, config.max_room_height)

        max_left = config.map_width - width
        max_top = config.map_height - height

        left = random.randint(0, max_left)
        top = random.randint(0, max_top)

        return Room(left=left, top=top, width=width, height=height)

    def _place_rooms(self) -> list[Room]:
        rooms = []
        config = self.config

        cell_width = config.map_width // 3
        cell_height = config.map_height // 3

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

    def _build_connections(self, rooms: Sequence[Room]) -> list[tuple[Room, Room]]:
        connections: list[tuple[Room, Room]] = []

        for row in range(3):
            base = row * 3
            connections.append((rooms[base + 0], rooms[base + 1]))
            connections.append((rooms[base + 1], rooms[base + 2]))

        for col in range(3):
            connections.append((rooms[col + 0], rooms[col + 3]))
            connections.append((rooms[col + 3], rooms[col + 6]))

        return connections

    def _carve_room(self, room, tiles):
        for y in range(room.top, room.bottom):
            for x in range(room.left, room.right):
                tiles[y][x] = TileFactory.floor()

    def _carve_corridor(self, room_a: Room, room_b: Room, tiles):
        ax, ay = self._select_door(room_a, room_b)
        bx, by = self._select_door(room_b, room_a)

        # горизонтальный участок
        for x in range(min(ax, bx), max(ax, bx)):
            tiles[ay][x] = TileFactory.corridor()

        # вертикальный участок
        for y in range(min(ay, by), max(ay, by)):
            tiles[y][bx] = TileFactory.corridor()

    def _select_door(self, a: Room, b: Room):
        ax, ay = a.center
        bx, by = b.center

        # B справа
        if bx > ax:
            return a.right, ay  # КЛЮЧЕВОЕ: точка находится ЗА границей комнаты

        # B слева
        if bx < ax:
            return a.left - 1, ay

        # B снизу
        if by > ay:
            return ax, a.bottom

        # B сверху
        if by < ay:
            return ax, a.top - 1

        return ax, ay  # fallback