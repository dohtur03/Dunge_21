from domain.map.room import Room

class Level:
    def __init__(self, width: int, height: int, rooms: list[Room]):
        self.width = width
        self.height = height
        self.rooms = rooms