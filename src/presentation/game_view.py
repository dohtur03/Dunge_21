import curses
import time


class GameView:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.PANEL_HEIGHT = 3
        # Опускаем границу защиты текста до 2-й строки,
        # чтобы 3-я строка была свободна для отрисовки верхних стен комнат
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
        # Теперь координаты и символ берутся из объекта player: game.player.y, game.player.x, game.player.char
        if 0 <= game.player.y < height and 0 <= game.player.x < width:
            self.stdscr.addch(game.player.y, game.player.x, game.player.char, curses.color_pair(7) | curses.A_BOLD)

    def draw_panel(self, game, height, width):
        active_buffs = []
        current_time = time.time()

        # Берем эффекты зелий теперь из игрока!
        for effect in game.player.potion_effects:
            if current_time < effect["end_time"]:
                active_buffs.append(f"{effect['type'].upper()}+{effect['value']}")

        if len(active_buffs) != 0:
            buffs_text = " | ".join(active_buffs[:3])
            if len(active_buffs) > 3:
                buffs_text += " + ..."
            status = f"Game started for {game.player.name}! Score: {game.player_score} Active buffs: {buffs_text}"
        else:
            status = f"Game started for {game.player.name}! Score: {game.player_score} No active buffs"

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
        # Панель интерфейса занимает координаты 0, 1 и 2.
        safe_y = 3

        wall_positions = set()  # Сюда мы будем сохранять координаты стен, чтобы делать в них двери
        room_floor_positions = set()  # NEW: Сюда мы сохраним координаты пола комнат, чтобы не перекрывать их

        # 1. Рисуем комнаты (Сначала пол и красивые двойные стены)
        for room in game.current_level.rooms:
            # Пол комнаты
            for ry in range(room.y, room.y + room.height):
                for rx in range(room.x, room.x + room.width):
                    if safe_y <= ry < height - 1 and 0 <= rx < width - 1:
                        self.stdscr.addch(ry, rx, '.', curses.color_pair(3))
                        room_floor_positions.add((ry, rx))  # NEW: Запоминаем координату пола

            # Верхняя и нижняя стены
            for rx in range(room.x - 1, room.x + room.width + 1):
                if safe_y <= room.y - 1 < height - 1 and 0 <= rx < width - 1:
                    self.stdscr.addch(room.y - 1, rx, '═', curses.color_pair(2) | curses.A_BOLD)
                    wall_positions.add((room.y - 1, rx))
                if safe_y <= room.y + room.height < height - 1 and 0 <= rx < width - 1:
                    self.stdscr.addch(room.y + room.height, rx, '═', curses.color_pair(2) | curses.A_BOLD)
                    wall_positions.add((room.y + room.height, rx))

            # Левая и правая стены
            for ry in range(room.y - 1, room.y + room.height + 1):
                if safe_y <= ry < height - 1 and 0 <= room.x - 1 < width - 1:
                    self.stdscr.addch(ry, room.x - 1, '║', curses.color_pair(2) | curses.A_BOLD)
                    wall_positions.add((ry, room.x - 1))
                if safe_y <= ry < height - 1 and 0 <= room.x + room.width < width - 1:
                    self.stdscr.addch(ry, room.x + room.width, '║', curses.color_pair(2) | curses.A_BOLD)
                    wall_positions.add((ry, room.x + room.width))

            # Углы комнат (добавлять их в wall_positions не нужно, они уже там)
            if safe_y <= room.y - 1 < height - 1:
                if 0 <= room.x - 1 < width - 1:
                    self.stdscr.addch(room.y - 1, room.x - 1, '╔', curses.color_pair(2) | curses.A_BOLD)
                if 0 <= room.x + room.width < width - 1:
                    self.stdscr.addch(room.y - 1, room.x + room.width, '╗', curses.color_pair(2) | curses.A_BOLD)

            if safe_y <= room.y + room.height < height - 1:
                if 0 <= room.x - 1 < width - 1:
                    self.stdscr.addch(room.y + room.height, room.x - 1, '╚', curses.color_pair(2) | curses.A_BOLD)
                if 0 <= room.x + room.width < width - 1:
                    self.stdscr.addch(room.y + room.height, room.x + room.width, '╝',
                                      curses.color_pair(2) | curses.A_BOLD)

            # 2. Рисуем коридоры и двери ПОВЕРХ, но умно
            for y, x in game.current_level.corridors:
                if safe_y <= y < height - 1 and 0 <= x < width - 1:
                    if (y, x) in wall_positions:
                        # Умная проверка: это настоящая дверь?
                        # Она должна вести в "чистый" коридор (не стену и не пол)
                        is_true_door = False
                        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            ny, nx = y + dy, x + dx
                            if (ny, nx) in game.current_level.corridors and \
                                    (ny, nx) not in wall_positions and \
                                    (ny, nx) not in room_floor_positions:
                                is_true_door = True
                                break

                        # Рисуем дверь только если она реально ведет наружу
                        if is_true_door:
                            self.stdscr.addch(y, x, '▦', curses.color_pair(4) | curses.A_BOLD)
                        # Если is_true_door == False, мы ничего не делаем,
                        # и на экране остается красивая стена ║ или ═, нарисованная в Шаге 1

                    elif (y, x) not in room_floor_positions:
                        # Темный пещерный коридор
                        self.stdscr.addch(y, x, '▒', curses.color_pair(3))

        # 3. Выход
        end_y, end_x = game.current_level.end_pos
        if safe_y <= end_y < height - 1 and 0 <= end_x < width - 1:
            self.stdscr.addch(end_y, end_x, '╬', curses.color_pair(7) | curses.A_BOLD)

        # 4. Рисуем предметы на полу
        char_map = {"Weapon": "†", "Potion": "ð", "Scroll": "§", "Food": "♣"}

        color_map = {"Weapon": 3, "Potion": 1, "Scroll": 2, "Food": 4}

        for (iy, ix), drop_info in game.current_level.item_drops.items():
            if safe_y <= iy < height - 1 and 0 <= ix < width - 1:
                category = drop_info["category"]

                # Достаем символ и цвет. Если категории нет в словаре — берем дефолты (* и белый цвет)
                char = char_map.get(category, "*")
                color_id = color_map.get(category, 7)

                # Рисуем с нужным цветом
                self.stdscr.addch(iy, ix, char, curses.color_pair(color_id) | curses.A_BOLD)

        # 5. Рисуем врагов
        for enemy in game.current_level.enemies:
            if safe_y <= enemy.y < height - 1 and 0 <= enemy.x < width - 1:
                if enemy.is_visible():
                    self.stdscr.addch(enemy.y, enemy.x, enemy.char,
                                      curses.color_pair(enemy.color_pair) | curses.A_BOLD)

    def draw_bottom_panel(self, game, height, width):
        # Хелпер: генератор красивых полосок прогресса
        def make_bar(current, maximum, length=10):
            if maximum <= 0: return f"[{'░' * length}]"
            # Считаем долю заполнения
            fill = int((current / maximum) * length)
            fill = min(max(fill, 0), length)  # Защита от переполнения
            return f"[{'█' * fill}{'░' * (length - fill)}]"

        # Генерируем полоски (15 символов для ХП, 10 для Опыта)
        hp_bar = make_bar(game.player.hits, game.player.max_hits, 15)
        exp_bar = make_bar(game.player.exp, game.player.exp_to_level_up, 10)

        # Оружие
        if game.player.current_weapon is None:
            weapon_str_hint = ""
        else:
            weapon_str_hint = f"(+{game.player.current_weapon.value})"

        # Собираем красивую и информативную строку с разделителями
        stats = (
            f"Stg:{game.player_stage} | "
            f"HP {hp_bar} {game.player.hits}/{game.player.max_hits} | "
            f"EXP {exp_bar} {game.player.exp}/{game.player.exp_to_level_up} | "
            f"Lvl:{game.player.level} | "
            f"Str:{game.player.str}{weapon_str_hint} | "
            f"Agi:{game.player.agility} | "
            f"Gold:${game.player.gold}"
        )

        y_stats = height - 1
        x_stats = max(1, (width - len(stats)) // 2)

        safe_width = width - x_stats - 1
        safe_stats = stats[:safe_width]

        # Очищаем строку перед отрисовкой, чтобы хвосты старых надписей не "прилипали"
        self.stdscr.move(y_stats, 0)
        self.stdscr.clrtoeol()

        # Рисуем!
        self.stdscr.addstr(y_stats, x_stats, safe_stats, curses.color_pair(3) | curses.A_BOLD)

    def show_exit_menu(self) -> int:
        # ... (Код этого метода остается без изменений)
        height, width = self.stdscr.getmaxyx()
        selected = 0
        blink = False

        while True:
            self.stdscr.clear()
            question = "Are you sure you want to leave the game?"
            q_y = height // 2
            q_x = (width - len(question)) // 2
            self.stdscr.addstr(q_y, q_x, question, curses.color_pair(3) | curses.A_BOLD)

            options_local = ["Yes", "No", "Back to menu"]
            pointer = "▶"

            for i, text in enumerate(options_local):
                y = q_y + 2 + i
                line = f"{pointer} {text}" if i == selected else f"  {text}"
                attr = (curses.color_pair(2 if blink else 3) | curses.A_BOLD) if i == selected else curses.color_pair(3)
                x = (width - len(line)) // 2
                self.stdscr.addstr(y, x, line, attr)

            self.stdscr.refresh()
            blink = not blink
            self.stdscr.timeout(300)
            key = self.stdscr.getch()

            if key == curses.KEY_UP:
                selected = (selected - 1) % len(options_local)
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % len(options_local)
            elif key in (curses.KEY_ENTER, 10, 13):
                return selected

    def show_victory_screen(self, game):
        height, width = self.stdscr.getmaxyx()
        self.stdscr.clear()

        # Красивые надписи
        title = "👑 YOU CONQUERED DUNGEON 21! 👑"
        subtitle = "The darkness recedes as you step into the sunlight..."
        stats = f"Final Score: {game.player_score} | Gold: {game.player.gold} | Level: {game.player.level}"
        hint = "< Press any key to return to the real world >"

        # Центрируем текст
        self.stdscr.addstr(height // 2 - 3, max(0, (width - len(title)) // 2), title,
                           curses.color_pair(2) | curses.A_BOLD)
        self.stdscr.addstr(height // 2 - 1, max(0, (width - len(subtitle)) // 2), subtitle, curses.color_pair(3))
        self.stdscr.addstr(height // 2 + 1, max(0, (width - len(stats)) // 2), stats,
                           curses.color_pair(4) | curses.A_BOLD)
        self.stdscr.addstr(height // 2 + 4, max(0, (width - len(hint)) // 2), hint,
                           curses.color_pair(3) | curses.A_BLINK)

        self.stdscr.refresh()

        # Ждем любого нажатия клавиши
        self.stdscr.timeout(-1)
        self.stdscr.getch()