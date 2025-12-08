import json

class LevelConfig:
    def __init__(
        self,
        map_width: int,
        map_height: int,
        rooms_in_row: int,
        rooms_in_column: int,
        min_room_width: int,
        max_room_width: int,
        min_room_height: int,
        max_room_height: int,
    ):
        self.map_width = map_width
        self.map_height = map_height

        self.rooms_in_row = rooms_in_row
        self.rooms_in_column = rooms_in_column

        self.min_room_width = min_room_width
        self.max_room_width = max_room_width

        self.min_room_height = min_room_height
        self.max_room_height = max_room_height

def load_config(path: str) -> LevelConfig:
    with open(path, "r") as file:
        data = json.load(file)
    return LevelConfig(**data)