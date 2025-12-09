import random

from domain.map.room import Room
from domain.map.level import Level
from domain.map.config import LevelConfig


class LevelGenerator:
    def __init__(self, config: LevelConfig):
        self.config = config

    def generate(self) -> Level:
        rooms = self._place_rooms()

        level = Level(
            width=self.config.map_width,
            height=self.config.map_height,
            rooms=rooms,
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