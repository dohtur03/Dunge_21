import curses
import time
from presentation.log import GameLog, death_message, get_random_message


class GameView:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.PANEL_HEIGHT = 3
        self.BORDER_TOP = 3
        self.logger = GameLog()

    def render(self, game):
        """Отрисовывает текущее состояние игры"""
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()

        # Корректируем координаты, чтобы игрок не вышел за рамки поля
        game.player_y = max(self.BORDER_TOP + 1, min(height - 3, game.player_y))
        game.player_x = max(1, min(width - 2, game.player_x))

        self.draw_panel(game, height, width)
        self.draw_field(height, width)
        self.draw_bottom_panel(game, height, width)
        self.draw_player(game)

        self.stdscr.refresh()

    def draw_player(self, game):
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
        x_status = (width - len(status)) // 2
        self.stdscr.addstr(y_status, x_status, status, curses.color_pair(4) | curses.A_BOLD)

        hint_controls = "<Press 'W', 'A', 'S', 'D' or arrows to move! ('q' to quit, 'i' to open inventory)>"
        y_hint_controls = y_status + 2
        x_hint_controls = (width - len(hint_controls)) // 2
        self.stdscr.addstr(y_hint_controls, x_hint_controls, hint_controls, curses.color_pair(3))

    def draw_field(self, height, width):
        top_line = "┌" + "─" * (width - 2) + "┐"
        self.stdscr.addstr(self.BORDER_TOP, 0, top_line[:width], curses.color_pair(2) | curses.A_BOLD)

        bot_line = "└" + "─" * (width - 2) + "┘"
        self.stdscr.addstr(height - 2, 0, bot_line[:width], curses.color_pair(2) | curses.A_BOLD)

        for y in range(self.BORDER_TOP + 1, height - 2):
            if 0 < width:
                self.stdscr.addch(y, 0, "│", curses.color_pair(2) | curses.A_BOLD)
            if width > 1:
                self.stdscr.addch(y, width - 1, "│", curses.color_pair(2) | curses.A_BOLD)

    def draw_bottom_panel(self, game, height, width):
        if game.current_weapon == None:
            weapon_str_hint = ""
        else:
            weapon_str = game.current_weapon.value
            weapon_str_hint = f"(+{weapon_str})"
        stats = f"Stage: {game.player_stage} Hits: {game.player_hits}/{game.player_max_hits} Str: {game.player_str}{weapon_str_hint} Agi: {game.player_agility} Gold: {game.player_gold} Exp: {game.player_exp}/{game.player_exp_to_level_up} Level: {game.player_level}"
        y_stats = height - 1
        x_stats = max(1, (width - len(stats)) // 2)
        self.stdscr.addstr(y_stats, x_stats, stats[:width], curses.color_pair(3) | curses.A_BOLD)

    def show_exit_menu(self) -> int:
        """Возвращает: 0 (Yes), 1 (No), 2 (Back to menu)"""
        height, width = self.stdscr.getmaxyx()
        selected = 1
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