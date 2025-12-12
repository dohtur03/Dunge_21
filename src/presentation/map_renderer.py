import curses

from domain.map.corridor import Corridor
from domain.map.level_exit import LevelExit
from domain.map.room import Room


class MapRenderer:
    def __init__(self, win):
        self.win = win

    def draw_level(self, level):
        self.win.erase()
        self.win.box()

        for room in level.rooms:
            self._draw_room(room)

        for corridor in level.corridors:
            self._draw_corridor(corridor)

        self._draw_level_exit(level.level_exit)

        self.win.refresh()

    def _draw_room(self, room: Room):
        for y in range(room.top, room.bottom):
            for x in range(room.left, room.right):
                try:
                    self.win.addch(y, x, ".")  # пол комнаты
                except curses.error:
                    pass

    def _draw_corridor(self, corridor: Corridor):
        for x, y in corridor.points:
            try:
                self.win.addch(y, x, ".")  # или другой символ для коридора
            except curses.error:
                pass
    def _draw_level_exit(self, level_exit: LevelExit):
        try:
            self.win.addch(level_exit.y, level_exit.x, "O")
        except curses.error:
            pass