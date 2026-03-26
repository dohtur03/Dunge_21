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

        self.draw_panel(game, height, width)
        self.draw_field(game, height, width)
        self.draw_bottom_panel(game, height, width)
        self.draw_player(game)

        self.stdscr.refresh()

    def draw_player(self, game):
        height, width = self.stdscr.getmaxyx()
        if 0 <= game.player.y < height and 0 <= game.player.x < width:
            self.stdscr.addch(game.player.y, game.player.x, game.player.char, curses.color_pair(7) | curses.A_BOLD)

    def draw_panel(self, game, height, width):
        active_buffs = []
        current_time = time.time()

        for effect in game.player.potion_effects:
            if current_time < effect["end_time"]:
                active_buffs.append(f"{effect['type'].upper()}+{effect['value']}")

        if len(active_buffs) != 0:
            buffs_text = " | ".join(active_buffs[:3])
            if len(active_buffs) > 3:
                buffs_text += " + ..."
            status = f"Game started for {game.player.name}! Score: {game.player.gold} Active buffs: {buffs_text}"
        else:
            status = f"Game started for {game.player.name}! Score: {game.player.gold} No active buffs"

        y_status = 0
        x_status = max(0, (width - len(status)) // 2)
        self.stdscr.addstr(y_status, x_status, status[:width - 1], curses.color_pair(4) | curses.A_BOLD)

        if hasattr(game, 'action_msg') and game.action_msg:
            hint_controls = f">>> {game.action_msg} <<<"
        else:
            hint_controls = "<Press 'W', 'A', 'S', 'D' or arrows to move! ('q' to quit, 'i' to open inventory)>"

        y_hint_controls = y_status + 2
        x_hint_controls = max(0, (width - len(hint_controls)) // 2)
        self.stdscr.addstr(y_hint_controls, x_hint_controls, hint_controls[:width - 1], curses.color_pair(3))

    def draw_field(self, game, height, width):
        safe_y = 3
        wall_positions = set()
        room_floor_positions = set()

        # --- СЛОЙ 1: ПОЛ И КОРИДОРЫ ---
        # Сначала собираем все клетки пола комнат
        for room in game.current_level.rooms:
            for ry in range(room.y, room.y + room.height):
                for rx in range(room.x, room.x + room.width):
                    if safe_y <= ry < height - 1 and 0 <= rx < width - 1:
                        room_floor_positions.add((ry, rx))
                        # Пол рисуем только если клетка видна ПРЯМО СЕЙЧАС
                        if (ry, rx) in game.fow.visible_cells:
                            self.stdscr.addch(ry, rx, '.', curses.color_pair(3))

        # Рисуем коридоры
        for y, x in game.current_level.corridors:
            if safe_y <= y < height - 1 and 0 <= x < width - 1:
                # Если клетка коридора не внутри комнаты
                if (y, x) not in room_floor_positions:
                    if (y, x) in game.fow.visible_cells:
                        # Яркий коридор в зоне видимости [cite: 313]
                        self.stdscr.addch(y, x, '▒', curses.color_pair(3))
                    elif (y, x) in game.fow.explored_cells:
                        # Тусклая точка для исследованного, но скрытого туманом коридора
                        self.stdscr.addch(y, x, '·', curses.color_pair(3))

        # --- СЛОЙ 2: СТЕНЫ КОМНАТ ---
        # Стены отображаются, если они были хоть раз исследованы
        for room in game.current_level.rooms:
            # Горизонтальные стены
            for rx in range(room.x - 1, room.x + room.width + 1):
                for ry in [room.y - 1, room.y + room.height]:
                    if safe_y <= ry < height - 1 and 0 <= rx < width - 1:
                        wall_positions.add((ry, rx))
                        if (ry, rx) in game.fow.explored_cells:
                            self.stdscr.addch(ry, rx, '═', curses.color_pair(2) | curses.A_BOLD)

            # Вертикальные стены
            for ry in range(room.y - 1, room.y + room.height + 1):
                for rx in [room.x - 1, room.x + room.width]:
                    if safe_y <= ry < height - 1 and 0 <= rx < width - 1:
                        wall_positions.add((ry, rx))
                        if (ry, rx) in game.fow.explored_cells:
                            self.stdscr.addch(ry, rx, '║', curses.color_pair(2) | curses.A_BOLD)

            # Углы комнат
            corners = [
                (room.y - 1, room.x - 1, '╔'), (room.y - 1, room.x + room.width, '╗'),
                (room.y + room.height, room.x - 1, '╚'), (room.y + room.height, room.x + room.width, '╝')
            ]
            for cy, cx, char in corners:
                if safe_y <= cy < height - 1 and 0 <= cx < width - 1:
                    if (cy, cx) in game.fow.explored_cells:
                        self.stdscr.addch(cy, cx, char, curses.color_pair(2) | curses.A_BOLD)

        # --- СЛОЙ 3: ДВЕРИ (ОБЫЧНЫЕ И ЗАПЕРТЫЕ) ---
        # 1. Обычные проемы (где коридор пересекает стену)
        for y, x in game.current_level.corridors:
            if (y, x) in wall_positions and (y, x) in game.fow.explored_cells:
                # Рисуем стандартный дверной проем
                self.stdscr.addch(y, x, '▦', curses.color_pair(4) | curses.A_BOLD)

        door_colors = {"Red": 1, "Blue": 7, "Yellow": 2}
        for (dy, dx), color_name in game.current_level.doors.items():
            if safe_y <= dy < height - 1 and 0 <= dx < width - 1:
                if (dy, dx) in game.fow.explored_cells:
                    c_pair = door_colors.get(color_name, 7)
                    self.stdscr.addch(dy, dx, '▦', curses.color_pair(c_pair) | curses.A_BOLD)

        end_y, end_x = game.current_level.end_pos
        if (end_y, end_x) in game.fow.explored_cells:
            self.stdscr.addch(end_y, end_x, '╬', curses.color_pair(7) | curses.A_BOLD)

        for (ky, kx), color_name in game.current_level.keys.items():
            if (ky, kx) in game.fow.visible_cells:
                c_pair = door_colors.get(color_name, 7)
                self.stdscr.addch(ky, kx, '⚷', curses.color_pair(c_pair) | curses.A_BOLD | curses.A_BLINK)

        # Предметы
        char_map = {"Weapon": "†", "Potion": "ð", "Scroll": "§", "Food": "♣"}
        color_map = {"Weapon": 3, "Potion": 1, "Scroll": 2, "Food": 4}
        for (iy, ix), drop_info in game.current_level.item_drops.items():
            if (iy, ix) in game.fow.visible_cells:
                category = drop_info["category"]
                char = char_map.get(category, "*")
                color_id = color_map.get(category, 7)
                self.stdscr.addch(iy, ix, char, curses.color_pair(color_id) | curses.A_BOLD)

        # Враги
        for enemy in game.current_level.enemies:
            if (enemy.y, enemy.x) in game.fow.visible_cells:
                if enemy.is_visible():
                    self.stdscr.addch(enemy.y, enemy.x, enemy.char,
                                      curses.color_pair(enemy.color_pair) | curses.A_BOLD)

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