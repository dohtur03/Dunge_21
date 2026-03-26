import curses
import time


class GameView:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.PANEL_HEIGHT = 3
        self.BORDER_TOP = 2

    def render(self, game):
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        map_h = 28
        map_w = 75

        off_y = max(3, (height - map_h) // 2)
        # Смещение по X
        off_x = max(0, (width - map_w) // 2)

        self.draw_panel(game, height, width)
        self.draw_field(game, height, width, off_y, off_x)
        self.draw_bottom_panel(game, height, width)
        self.draw_player(game, off_y, off_x)

        self.stdscr.refresh()

    def draw_player(self, game, off_y, off_x):
        height, width = self.stdscr.getmaxyx()
        # Прибавляем смещение к координатам игрока
        py, px = game.player.y + off_y, game.player.x + off_x
        if 0 <= py < height and 0 <= px < width:
            self.stdscr.addch(py, px, game.player.char, curses.color_pair(7) | curses.A_BOLD)

    def draw_panel(self, game, height, width):
        active_buffs = []
        current_time = time.time()

        for effect in game.player.potion_effects:
            if current_time < effect["end_time"]:
                active_buffs.append(f"{effect['type'].upper()}+{effect['value']}")

        if active_buffs:
            buffs_text = " | ".join(active_buffs[:3])
            status = f"Hero: {game.player.name} | Score: {game.player.gold} | Buffs: {buffs_text}"
        else:
            status = f"Hero: {game.player.name} | Score: {game.player.gold} | No active buffs"

        y_status = 0
        x_status = max(0, (width - len(status)) // 2)
        self.stdscr.addstr(y_status, x_status, status[:width - 1], curses.color_pair(4) | curses.A_BOLD)


        if hasattr(game, 'action_msg') and game.action_msg:
            msg = f">>> {game.action_msg} <<<"
            y_msg = y_status + 1
            x_msg = max(0, (width - len(msg)) // 2)
            self.stdscr.addstr(y_msg, x_msg, msg[:width - 1], curses.color_pair(2) | curses.A_BOLD)

        controls = (
            "[Arrows/WASD]:Move [i]:Inventory  "
            "[h]:Weapon  [k]:Potion  [e]:Scroll  [j]:Food  "
            "[q]:Quit"
        )

        y_controls = y_status + 2
        x_controls = max(0, (width - len(controls)) // 2)

        # Печатаем подсказку (используем тусклый цвет, чтобы не отвлекала от игры)
        self.stdscr.addstr(y_controls, x_controls, controls[:width - 1], curses.color_pair(3))

    def draw_field(self, game, height, width, off_y, off_x):
        wall_positions = set()
        room_floor_positions = set()

        # --- СЛОЙ 1: ПОЛ И КОРИДОРЫ ---
        for room in game.current_level.rooms:
            for ry in range(room.y, room.y + room.height):
                for rx in range(room.x, room.x + room.width):
                    # Применяем смещение
                    dy, dx = ry + off_y, rx + off_x
                    if 0 <= dy < height - 1 and 0 <= dx < width - 1:
                        room_floor_positions.add((ry, rx))
                        if (ry, rx) in game.fow.visible_cells:
                            self.stdscr.addch(dy, dx, '.', curses.color_pair(3))

        for y, x in game.current_level.corridors:
            dy, dx = y + off_y, x + off_x
            if 0 <= dy < height - 1 and 0 <= dx < width - 1:
                if (y, x) not in room_floor_positions:
                    if (y, x) in game.fow.visible_cells:
                        self.stdscr.addch(dy, dx, '▒', curses.color_pair(3))
                    elif (y, x) in game.fow.explored_cells:
                        self.stdscr.addch(dy, dx, '·', curses.color_pair(3))

        # --- СЛОЙ 2: СТЕНЫ ---
        for room in game.current_level.rooms:
            # Горизонтальные
            for rx in range(room.x - 1, room.x + room.width + 1):
                for ry in [room.y - 1, room.y + room.height]:
                    dy, dx = ry + off_y, rx + off_x
                    if 0 <= dy < height - 1 and 0 <= dx < width - 1:
                        wall_positions.add((ry, rx))
                        if (ry, rx) in game.fow.explored_cells:
                            self.stdscr.addch(dy, dx, '═', curses.color_pair(2) | curses.A_BOLD)
            # Вертикальные
            for ry in range(room.y - 1, room.y + room.height + 1):
                for rx in [room.x - 1, room.x + room.width]:
                    dy, dx = ry + off_y, rx + off_x
                    if 0 <= dy < height - 1 and 0 <= dx < width - 1:
                        wall_positions.add((ry, rx))
                        if (ry, rx) in game.fow.explored_cells:
                            self.stdscr.addch(dy, dx, '║', curses.color_pair(2) | curses.A_BOLD)
            # Углы
            corners = [
                (room.y - 1, room.x - 1, '╔'), (room.y - 1, room.x + room.width, '╗'),
                (room.y + room.height, room.x - 1, '╚'), (room.y + room.height, room.x + room.width, '╝')
            ]
            for cy, cx, char in corners:
                dy, dx = cy + off_y, cx + off_x
                if 0 <= dy < height - 1 and 0 <= dx < width - 1:
                    if (cy, cx) in game.fow.explored_cells:
                        self.stdscr.addch(dy, dx, char, curses.color_pair(2) | curses.A_BOLD)

        # --- СЛОЙ 3: ДВЕРИ И ВЫХОД ---
        door_colors = {"Red": 1, "Blue": 7, "Yellow": 2}
        # Обычные проемы
        for y, x in game.current_level.corridors:
            dy, dx = y + off_y, x + off_x
            if (y, x) in wall_positions and (y, x) in game.fow.explored_cells:
                if 0 <= dy < height - 1 and 0 <= dx < width - 1:
                    self.stdscr.addch(dy, dx, '▦', curses.color_pair(4) | curses.A_BOLD)

        # Цветные двери
        for (dy_map, dx_map), color_name in game.current_level.doors.items():
            dy, dx = dy_map + off_y, dx_map + off_x
            if 0 <= dy < height - 1 and 0 <= dx < width - 1:
                if (dy_map, dx_map) in game.fow.explored_cells:
                    c_pair = door_colors.get(color_name, 7)
                    self.stdscr.addch(dy, dx, '▦', curses.color_pair(c_pair) | curses.A_BOLD)

        # Выход
        ey_map, ex_map = game.current_level.end_pos
        ey, ex = ey_map + off_y, ex_map + off_x
        if 0 <= ey < height - 1 and 0 <= ex < width - 1:
            if (ey_map, ex_map) in game.fow.explored_cells:
                self.stdscr.addch(ey, ex, '╬', curses.color_pair(7) | curses.A_BOLD)

        # --- СЛОЙ 4: ПРЕДМЕТЫ И ВРАГИ ---
        # Ключи
        for (ky_map, kx_map), color_name in game.current_level.keys.items():
            ky, kx = ky_map + off_y, kx_map + off_x
            if 0 <= ky < height - 1 and 0 <= kx < width - 1:
                if (ky_map, kx_map) in game.fow.visible_cells:
                    try:
                        c_pair = door_colors.get(color_name, 7)
                        self.stdscr.addstr(ky, kx, '⚷', curses.color_pair(c_pair) | curses.A_BOLD | curses.A_BLINK)
                    except curses.error:
                        pass

        # Предметы
        char_map = {"Weapon": "†", "Potion": "ð", "Scroll": "§", "Food": "♣"}
        color_map = {"Weapon": 3, "Potion": 1, "Scroll": 2, "Food": 4}
        for (iy_map, ix_map), drop_info in game.current_level.item_drops.items():
            iy, ix = iy_map + off_y, ix_map + off_x
            if 0 <= iy < height - 1 and 0 <= ix < width - 1:
                if (iy_map, ix_map) in game.fow.visible_cells:
                    try:
                        category = drop_info["category"]
                        self.stdscr.addstr(iy, ix, char_map.get(category, "*"),
                                           curses.color_pair(color_map.get(category, 7)) | curses.A_BOLD)
                    except curses.error:
                        pass

        # Враги
        for enemy in game.current_level.enemies:
            ey, ex = enemy.y + off_y, enemy.x + off_x
            if 0 <= ey < height - 1 and 0 <= ex < width - 1:
                if (enemy.y, enemy.x) in game.fow.visible_cells:
                    if enemy.is_visible():
                        try:
                            self.stdscr.addch(ey, ex, enemy.char,
                                              curses.color_pair(enemy.color_pair) | curses.A_BOLD)
                        except curses.error:
                            pass

    def draw_bottom_panel(self, game, height, width):
        def make_bar(current, maximum, length=10):
            if maximum <= 0: return f"[{'░' * length}]"
            fill = min(max(int((current / maximum) * length), 0), length)
            return f"[{'█' * fill}{'░' * (length - fill)}]"

        hp_bar = make_bar(game.player.hits, game.player.max_hits, 15)
        exp_bar = make_bar(game.player.exp, game.player.exp_to_level_up, 10)
        weapon_hint = f"(+{game.player.current_weapon.value})" if game.player.current_weapon else ""

        stats = (
            f"Stg:{game.player_stage} | HP {hp_bar} {game.player.hits}/{game.player.max_hits} | "
            f"EXP {exp_bar} {game.player.exp}/{game.player.exp_to_level_up} | "
            f"Lvl:{game.player.level} | Str:{game.player.str}{weapon_hint} | "
            f"Agi:{game.player.agility} | Gold:${game.player.gold}"
        )

        y_stats = height - 1
        x_stats = max(1, (width - len(stats)) // 2)
        self.stdscr.move(y_stats, 0)
        self.stdscr.clrtoeol()
        self.stdscr.addstr(y_stats, x_stats, stats[:width - x_stats - 1], curses.color_pair(3) | curses.A_BOLD)

    def show_exit_menu(self) -> int:
        height, width = self.stdscr.getmaxyx()
        selected, blink = 0, False
        while True:
            self.stdscr.clear()
            question = "Are you sure you want to leave the game?"
            self.stdscr.addstr(height // 2, (width - len(question)) // 2, question, curses.color_pair(3) | curses.A_BOLD)
            opts = ["Yes", "No", "Back to menu"]
            for i, text in enumerate(opts):
                line = f"▶ {text}" if i == selected else f"  {text}"
                attr = (curses.color_pair(2 if blink else 3) | curses.A_BOLD) if i == selected else curses.color_pair(3)
                self.stdscr.addstr(height // 2 + 2 + i, (width - len(line)) // 2, line, attr)
            self.stdscr.refresh()
            blink = not blink
            self.stdscr.timeout(300)
            key = self.stdscr.getch()
            if key == curses.KEY_UP: selected = (selected - 1) % len(opts)
            elif key == curses.KEY_DOWN: selected = (selected + 1) % len(opts)
            elif key in (curses.KEY_ENTER, 10, 13): return selected

    def show_victory_screen(self, game):
        height, width = self.stdscr.getmaxyx()
        self.stdscr.clear()
        title = "👑 YOU CONQUERED DUNGEON 21! 👑"
        subtitle = "The darkness recedes as you step into the sunlight..."
        stats = f"Final Score: {game.get_score()} | Gold: {game.player.gold} | Level: {game.player.level}"
        hint = "< Press any key to return to the real world >"

        self.stdscr.addstr(height // 2 - 3, max(0, (width - len(title)) // 2), title, curses.color_pair(2) | curses.A_BOLD)
        self.stdscr.addstr(height // 2 - 1, max(0, (width - len(subtitle)) // 2), subtitle, curses.color_pair(3))
        self.stdscr.addstr(height // 2 + 1, max(0, (width - len(stats)) // 2), stats, curses.color_pair(4) | curses.A_BOLD)
        self.stdscr.addstr(height // 2 + 4, max(0, (width - len(hint)) // 2), hint, curses.color_pair(3) | curses.A_BLINK)
        self.stdscr.refresh()
        self.stdscr.timeout(-1)
        self.stdscr.getch()