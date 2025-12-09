import curses

class MapRenderer:
    def __init__(self, win):
        self.win = win

    def draw_level(self, level):
        # очистить окно
        self.win.erase()
        self.win.box()

        for room in level.rooms:
            self._draw_room(room)

        self.win.refresh()

    def _draw_room(self, room):
        for y in range(room.top, room.bottom):
            for x in range(room.left, room.right):
                try:
                    self.win.addch(y, x, ".")
                except curses.error:
                    pass