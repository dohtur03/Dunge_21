import curses
import time
from presentation.log import GameLog


class GameView:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.PANEL_HEIGHT = 3
        # Опускаем границу защиты текста до 2-й строки,
        # чтобы 3-я строка была свободна для отрисовки верхних стен комнат
        self.BORDER_TOP = 2
        self.logger = GameLog()

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
        if 0 <= game.player_y < height and 0 <= game.player_x < width:
            self.stdscr.addch(game.player_y, game.player_x, game.player_char, curses.color_pair(7) | curses.A_BOLD)

    def draw_panel(self, game, height, width):
        active_buffs = []
        current_time = time.time()
        for effect in game.potion_effects:
            if current_time < effect["end_time"]:
                active_buffs.append(f"{effect['type'].upper()}+{effect['value']}")

        if len(active_buffs) != 0:
            buffs_text = " | ".join(active_buffs[:3])
            if len(active_buffs) > 3:
                buffs_text += " + ..."
            status = f"Game started for {game.player_name}! Score: {game.player_score} Active buffs: {buffs_text}"
        else:
            status = f"Game started for {game.player_name}! Score: {game.player_score} No active buffs"

        y_status = 0
        x_status = max(0, (width - len(status)) // 2)
        self.stdscr.addstr(y_status, x_status, status[:width - 1], curses.color_pair(4) | curses.A_BOLD)

        hint_controls = "<Press 'W', 'A', 'S', 'D' or arrows to move! ('q' to quit, 'i' to open inventory)>"
        y_hint_controls = y_status + 2
        x_hint_controls = max(0, (width - len(hint_controls)) // 2)
        self.stdscr.addstr(y_hint_controls, x_hint_controls, hint_controls[:width - 1], curses.color_pair(3))

    def draw_field(self, game, height, width):
        # Панель интерфейса занимает координаты 0, 1 и 2.
        # Координата 3 — это первая безопасная линия для вывода графики.
        safe_y = 3

        # 1. Рисуем коридоры
        for y, x in game.current_level.corridors:
            if safe_y <= y < height - 1 and 0 <= x < width - 1:
                self.stdscr.addch(y, x, '#', curses.color_pair(3))

        # 2. Рисуем комнаты
        for room in game.current_level.rooms:
            # Пол комнаты
            for ry in range(room.y, room.y + room.height):
                for rx in range(room.x, room.x + room.width):
                    if safe_y <= ry < height - 1 and 0 <= rx < width - 1:
                        self.stdscr.addch(ry, rx, '.', curses.color_pair(3))

            # Верхняя и нижняя стены
            for rx in range(room.x - 1, room.x + room.width + 1):
                if safe_y <= room.y - 1 < height - 1 and 0 <= rx < width - 1:
                    self.stdscr.addch(room.y - 1, rx, '─', curses.color_pair(2))
                if safe_y <= room.y + room.height < height - 1 and 0 <= rx < width - 1:
                    self.stdscr.addch(room.y + room.height, rx, '─', curses.color_pair(2))

            # Левая и правая стены
            for ry in range(room.y - 1, room.y + room.height + 1):
                if safe_y <= ry < height - 1 and 0 <= room.x - 1 < width - 1:
                    self.stdscr.addch(ry, room.x - 1, '│', curses.color_pair(2))
                if safe_y <= ry < height - 1 and 0 <= room.x + room.width < width - 1:
                    self.stdscr.addch(ry, room.x + room.width, '│', curses.color_pair(2))

            # Углы комнат
            if safe_y <= room.y - 1 < height - 1:
                if 0 <= room.x - 1 < width - 1:
                    self.stdscr.addch(room.y - 1, room.x - 1, '┌', curses.color_pair(2))
                if 0 <= room.x + room.width < width - 1:
                    self.stdscr.addch(room.y - 1, room.x + room.width, '┐', curses.color_pair(2))

            if safe_y <= room.y + room.height < height - 1:
                if 0 <= room.x - 1 < width - 1:
                    self.stdscr.addch(room.y + room.height, room.x - 1, '└', curses.color_pair(2))
                if 0 <= room.x + room.width < width - 1:
                    self.stdscr.addch(room.y + room.height, room.x + room.width, '┘', curses.color_pair(2))


        # 3. Выход
        end_y, end_x = game.current_level.end_pos
        if safe_y <= end_y < height - 1 and 0 <= end_x < width - 1:
            self.stdscr.addch(end_y, end_x, '>', curses.color_pair(4) | curses.A_BOLD)

        # 4. Рисуем золото (Символ '$', цвет 4 - обычно желтый)
        for (gy, gx), amount in game.current_level.gold_drops.items():
            if safe_y <= gy < height - 1 and 0 <= gx < width - 1:
                self.stdscr.addch(gy, gx, '$', curses.color_pair(4) | curses.A_BOLD)

        # 5. Рисуем врагов (Цвет 1 - красный)
        for enemy in game.current_level.enemies:
            if safe_y <= enemy.y < height - 1 and 0 <= enemy.x < width - 1:
                self.stdscr.addch(enemy.y, enemy.x, enemy.char, curses.color_pair(1) | curses.A_BOLD)

    def draw_bottom_panel(self, game, height, width):
        if game.current_weapon == None:
            weapon_str_hint = ""
        else:
            weapon_str_hint = f"(+{game.current_weapon.value})"

        stats = f"Stage: {game.player_stage} Hits: {game.player_hits}/{game.player_max_hits} Str: {game.player_str}{weapon_str_hint} Agi: {game.player_agility} Gold: {game.player_gold} Exp: {game.player_exp}/{game.player_exp_to_level_up} Level: {game.player_level}"
        y_stats = height - 1
        x_stats = max(1, (width - len(stats)) // 2)

        # ЖЕСТКАЯ ЗАЩИТА ОТ СКРОЛЛА: обрезаем строку так, чтобы она точно не задела правый нижний край
        safe_width = width - x_stats - 1
        safe_stats = stats[:safe_width]

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