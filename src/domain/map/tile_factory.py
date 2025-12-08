from domain.map.tile import Tile

class TileFactory:
    @staticmethod
    def empty():
        return Tile(" ")

    @staticmethod
    def floor():
        return Tile(".")

    @staticmethod
    def corridor():
        return Tile(",")

    @staticmethod
    def wall():
        return Tile("#")