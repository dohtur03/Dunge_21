import curses

from domain.map.config import load_config
from domain.map.generator import LevelGenerator
from presentation.map_renderer import MapRenderer


class Session:
    def start(self, stdscr):
        curses.curs_set(0)

        # Загрузка конфигурации уровня
        config = load_config("domain/map/level.cfg")

        map_height = config.map_height
        map_width = config.map_width

        # создаём окно карты
        map_win = curses.newwin(map_height, map_width, 0, 0)
        map_win.box()

        # Генерация уровня
        generator = LevelGenerator(config)
        level = generator.generate()

        renderer = MapRenderer(map_win)

        renderer.draw_level(level)
        map_win.refresh()

        map_win.getch()