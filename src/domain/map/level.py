from domain.map.room import Room
from domain.map.tile_factory import TileFactory

class Level:
    def __init__(self, width: int, height: int, rooms: list[Room], connections: list[tuple[Room, Room]]):
        self.width = width
        self.height = height
        self.rooms = rooms
        self.connections = connections

        self.tiles = [
            [TileFactory.empty() for _ in range(width)]
            for _ in range(height)
        ]