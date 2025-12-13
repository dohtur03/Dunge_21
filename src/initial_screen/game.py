import curses
from log import *
import time
from inventory import *

class Game:
    def __init__(self, stdscr, player_name: str):
        self.stdscr = stdscr
        self.stdscr.keypad(True)
        self.player_name = player_name
        self.player_y = 0
        self.player_x = 0
        self.player_char = "☺"
        self.player_score = 0
        self.player_stage = 1
        self.player_hits = 20
        self.player_str = 10
        self.player_agility = 10
        self.player_gold = 10
        self.player_exp = 0
        self.player_level = 1

        height, width = stdscr.getmaxyx()
        self.player_pos_init(height, width)

        self.PANEL_HEIGHT = 3
        self.BORDER_TOP = 3

        self.logger = GameLog()

        self.inventory = Inventory(stdscr, player_name)

    @classmethod
    def from_slot(cls, stdscr, slot_name: str):
        game = cls(stdscr, f"Player_{slot_name}")
        return game

    def get_score(self):
        return self.player_score

    def exit_game(self) -> int:
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

                if i == selected:
                    color = curses.color_pair(2 if blink else 3)
                    attr = color | curses.A_BOLD
                else:
                    attr = curses.color_pair(3)

                x = (width - len(line)) // 2
                self.stdscr.addstr(y, x, line, attr)

            self.stdscr.refresh()

            blink = not blink
            self.stdscr.timeout(300)
            key = self.stdscr.getch()

            if key == -1:
                continue
            if key == curses.KEY_UP:
                selected = (selected - 1) % len(options_local)
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % len(options_local)
            elif key in (curses.KEY_ENTER, 10, 13):
                return selected

    def run(self) -> str:
        while True:
            current_time = time.time()
            
            if self.logger.needs_popup(current_time):
                msg = get_random_message()
                self.logger.show_popup(self.stdscr, msg)
                self.logger.last_popup = current_time
            
            self.stdscr.timeout(100)
            key = self.stdscr.getch()
            
            if key == ord('q'):
                option = self.exit_game()
                if option == 0:
                    self.stdscr.clear()
                    msg = "Good luck! See you next time!"
                    h, w = self.stdscr.getmaxyx()
                    y = h // 2
                    x = (w - len(msg)) // 2
                    self.stdscr.addstr(y, x, msg, curses.color_pair(3) | curses.A_BOLD)
                    self.stdscr.refresh()
                    self.stdscr.timeout(-1)
                    self.stdscr.getch()
                    return "quit_game"
                if option == 1:
                    continue
                if option == 2:
                    return "back_to_menu"
            elif key == ord('i'):
                selected_category = self.inventory.show()
                if selected_category and selected_category != "Back":
                    self.open_category(selected_category)
            elif key == ord('w') or key == curses.KEY_UP:
                self.player_y -= 1
            elif key == ord('s') or key == curses.KEY_DOWN:
                self.player_y += 1
            elif key == ord('a') or key == curses.KEY_LEFT:
                self.player_x -= 1
            elif key == ord('d') or key == curses.KEY_RIGHT:
                self.player_x += 1
        
            self.draw_game()
            
    def player_pos_init(self, height, width):
        self.player_y = height // 2
        self.player_x = width // 2

    def draw_player(self) -> None:
        self.stdscr.addch(self.player_y, self.player_x, self.player_char, curses.color_pair(7) | curses.A_BOLD)

    def draw_panel(self, height, width) -> None:
        status = f"Game started for {self.player_name}! Score: {self.player_score}"
        y_status = 0
        x_status = (width - len(status)) // 2
        self.stdscr.addstr(y_status, x_status, status, curses.color_pair(4) | curses.A_BOLD)

        hint_controls = "<Press 'W', 'A', 'S', 'D' or arrows to move! ('q' to quit, 'i' to open inventory)>"
        y_hint_controls = y_status + 2
        x_hint_controls = (width - len(hint_controls)) // 2
        self.stdscr.addstr(y_hint_controls, x_hint_controls, hint_controls, curses.color_pair(3))

    def draw_field(self, height, width) -> None:
        top_line = "┌" + "─" * (width - 2) + "┐"
        self.stdscr.addstr(self.BORDER_TOP, 0, top_line[:width], curses.color_pair(2) | curses.A_BOLD)

        bot_line = "└" + "─" * (width - 2) + "┘"
        self.stdscr.addstr(height - 2, 0, bot_line[:width], curses.color_pair(2) | curses.A_BOLD)

        for y in range(self.BORDER_TOP + 1, height - 2):
            if 0 < width:
                self.stdscr.addch(y, 0, "│", curses.color_pair(2) | curses.A_BOLD)
            if width > 1:
                self.stdscr.addch(y, width - 1, "│", curses.color_pair(2) | curses.A_BOLD)

    def draw_bottom_panel(self, height, width) -> None:
        stats = f"Stage: {self.player_stage} Hits: {self.player_hits} Str: {self.player_str} Agi: {self.player_agility} Gold: {self.player_gold} Exp: {self.player_exp} Level: {self.player_level}"
        y_stats = height - 1
        x_stats = max(1, (width - len(stats)) // 2)
        self.stdscr.addstr(y_stats, x_stats, stats[:width], curses.color_pair(3) | curses.A_BOLD)
        
    def draw_game(self) -> None:
        self.stdscr.clear()
            
        height, width = self.stdscr.getmaxyx()
        
        self.player_y = max(self.BORDER_TOP + 1, min(height - 3, self.player_y))
        self.player_x = max(1, min(width - 2, self.player_x))
        
        self.draw_panel(height, width)
        self.draw_field(height, width)
        self.draw_bottom_panel(height, width)
        self.draw_player()

        self.stdscr.refresh()
    
    def open_category(self, category: str) -> None:
        chosen_item = self.inventory.show_category_items(category)
        if chosen_item is None:
            return
        
        height, width = self.stdscr.getmaxyx()
        msg = f"{category}: {chosen_item}"
        y = height // 2
        x = (width - len(msg)) // 2
        self.stdscr.clear()
        self.stdscr.addstr(y, x, msg, curses.color_pair(4) | curses.A_BOLD)
        self.stdscr.refresh()
        self.stdscr.timeout(-1)
        self.stdscr.getch()