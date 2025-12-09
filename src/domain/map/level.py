from domain.map.room import Room
from domain.map.corridor import Corridor

class Level:
    def __init__(self, width: int, height: int, rooms: list[Room], connections: list[tuple[Room, Room]], corridors: list[Corridor]):
        self.width = width
        self.height = height
        self.rooms = rooms
        self.connections = connections
        self.corridors = corridors