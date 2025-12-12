from domain.map.room import Room
from domain.map.corridor import Corridor
from domain.map.level_exit import LevelExit

class Level:
    def __init__(self, width: int, height: int, rooms: list[Room], connections: list[tuple[Room, Room]], corridors: list[Corridor], level_exit: LevelExit):
        self.width = width
        self.height = height
        self.rooms = rooms
        self.connections = connections
        self.corridors = corridors
        self.level_exit = level_exit