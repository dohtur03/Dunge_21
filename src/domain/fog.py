import math


class FogOfWar:
    def __init__(self):
        self.visible_cells = set()
        self.explored_cells = set()
        self.explored_rooms = set()

    def reset(self):
        """Очищает память при переходе на новый этаж"""
        self.visible_cells.clear()
        self.explored_cells.clear()
        self.explored_rooms.clear()

    def update(self, player_y: int, player_x: int, level):
        self.visible_cells.clear()
        self.visible_cells.add((player_y, player_x))
        self.explored_cells.add((player_y, player_x))

        # 1. ВСЕГДА пускаем лучи, чтобы видеть коридоры через двери
        radius = 6  # Немного увеличим радиус обзора
        for angle in range(0, 360, 4):  # Чаще лучи — лучше точность
            rad = math.radians(angle)
            dy, dx = math.sin(rad), math.cos(rad)
            self._cast_ray(player_y, player_x, dy, dx, radius, level)

        # 2. Если мы в комнате — подсвечиваем её целиком (как в Rogue)
        current_room = None
        for room in level.rooms:
            if room.y <= player_y < room.y + room.height and room.x <= player_x < room.x + room.width:
                current_room = room
                break

        if current_room:
            self.explored_rooms.add(current_room)
            for ry in range(current_room.y - 1, current_room.y + current_room.height + 1):
                for rx in range(current_room.x - 1, current_room.x + current_room.width + 1):
                    self.visible_cells.add((ry, rx))
                    self.explored_cells.add((ry, rx))

    def _cast_ray(self, sy: int, sx: int, dy: float, dx: float, radius: int, level):
        """Пускает один луч до препятствия или конца радиуса"""
        for i in range(1, radius + 1):
            ny, nx = int(sy + dy * i), int(sx + dx * i)
            self.visible_cells.add((ny, nx))
            self.explored_cells.add((ny, nx))

            # Проверяем, блокирует ли клетка свет
            is_wall = True
            if (ny, nx) in level.corridors:
                is_wall = False
            for room in level.rooms:
                if room.y <= ny < room.y + room.height and room.x <= nx < room.x + room.width:
                    is_wall = False
                    break

            if (ny, nx) in level.doors:
                is_wall = True  # Цветные двери блокируют свет

            if is_wall:
                break  # Луч ударился в стену