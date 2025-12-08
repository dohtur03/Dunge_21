import curses

class MapRenderer:
    def __init__(self, win):
        self.win = win

    def draw_level(self, level):
        # реальные размеры окна
        height, width = self.win.getmaxyx()

        # не выходим за пределы окна (мин с запасом)
        max_y = min(level.height, height) - 1
        max_x = min(level.width, width) - 1

        for y in range(max_y):
            for x in range(max_x):
                ch = level.tiles[y][x].char
                try:
                    self.win.addch(y, x, ch)
                except curses.error:
                    # если всё-таки что-то пошло не так — просто игнорируем
                    pass