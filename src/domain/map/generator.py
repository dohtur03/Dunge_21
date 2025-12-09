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
        connections: list[tuple[Room, Room]] = []

        rows = self.config.rooms_in_row
        cols = self.config.rooms_in_column

        for row in range(rows):
            for col in range(cols - 1):
                idx_left = row * cols + col
                idx_right = row * cols + (col + 1)
                connections.append((rooms[idx_left], rooms[idx_right]))

        for row in range(rows - 1):
            for col in range(cols):
                idx_top = row * cols + col
                idx_bottom = (row + 1) * cols + col
                connections.append((rooms[idx_top], rooms[idx_bottom]))

        return connections