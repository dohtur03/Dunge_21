import curses
from draw import *

player_name = "<default_player>" # потом импортировать из класса Player наверное будем

class Menu():
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_YELLOW, -1)
        curses.init_pair(3, curses.COLOR_WHITE, -1)
        curses.init_pair(4, curses.COLOR_GREEN, -1)
        curses.init_pair(5, curses.COLOR_BLUE, -1)
        curses.init_pair(6, curses.COLOR_MAGENTA, -1)
        curses.init_pair(7, curses.COLOR_CYAN, -1)
        curses.init_pair(8, curses.COLOR_BLACK, -1)
        self.sound_on = True
    
    def load_game(self) -> str | None:
        height, width = self.stdscr.getmaxyx()
        selected = 0
        blink = False

        slots = ["<test_slot>"] + ["<empty>"] * 9 + ["Back"]
        back_index = len(slots) - 1

        while True:
            self.stdscr.clear()
            big_block = big_load_game
            block_h = len(big_block)
            y_title = height // 4 - block_h // 2
            
            for i, line in enumerate(big_block):
                y = y_title + i
                if 0 <= y < height:
                    x = (width - len(line)) // 2
                    self.stdscr.addstr(y, x, line,  curses.color_pair(2) | curses.A_BOLD)
            
            options_h = len(slots)
            center_y = height // 2
            first_y = center_y - options_h // 2

            pointer = "▶"

            for i, name in enumerate(slots):
                y = first_y + i
                if y < 0 or y >= height:
                    continue

                is_selected = (i == selected)
                is_back = (i == back_index)
                is_empty = (name == "<empty>")

                line = f"{pointer} {name}" if is_selected else f"  {name}"

                if is_selected:
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
                selected = (selected - 1) % len(slots)
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % len(slots)
            elif key in (curses.KEY_ENTER, 10, 13):
                if selected == back_index:
                    return None
                if slots[selected] == "<empty>":
                    continue
                return slots[selected].strip("<>")

    def score_menu(self) -> None:
        height, width = self.stdscr.getmaxyx()
        selected = 0
        blink = False

        while True:
            self.stdscr.clear()

            big_block = big_score
            block_h = len(big_block)
            y_title = height // 4 - block_h // 2

            for i, line in enumerate(big_block):
                y = y_title + i
                if 0 <= y < height:
                    x = (width - len(line)) // 2
                    self.stdscr.addstr(y, x, line, curses.color_pair(2) | curses.A_BOLD)

            options_h = 1
            center_y = height // 2
            y_back = center_y - options_h // 2

            pointer = "▶" if selected == 0 else " "
            line_back = f"{pointer} Back"

            color_back = curses.color_pair(2 if (selected == 0 and blink) else 3)
            attr_back = color_back | (curses.A_BOLD if selected == 0 else 0)
            x_back = (width - len(line_back)) // 2
            self.stdscr.addstr(y_back, x_back, line_back, attr_back)

            self.stdscr.refresh()

            blink = not blink
            self.stdscr.timeout(300)
            key = self.stdscr.getch()

            if key == -1:
                continue
            if key in (curses.KEY_UP, curses.KEY_DOWN):
                selected = (selected + 1) % 1
            elif key in (curses.KEY_ENTER, 10, 13):
                return
    
    def settings_menu(self) -> None:
        height, width = self.stdscr.getmaxyx()
        selected = 0
        blink = False

        while True:
            self.stdscr.clear()
            
            height, width = self.stdscr.getmaxyx()
            big_block = big_settings
            block_h = len(big_block)
            y_title = height // 4 - block_h // 2

            for i, line in enumerate(big_block):
                y = y_title + i
                if 0 <= y < height:
                    x = (width - len(line)) // 2
                    self.stdscr.addstr(y, x, line, curses.color_pair(2) | curses.A_BOLD)

            options_h = 2
            center_y = height // 2
            y_sound = center_y - options_h // 2
            y_back  = y_sound + 2
            
            sound_text = f"Sound: {'ON' if self.sound_on else 'OFF'}"
            pointer = "▶" if selected == 0 else " "
            line_sound = f"{pointer} {sound_text}"

            color_sound = curses.color_pair(2 if (selected == 0 and blink) else 3)
            attr_sound = color_sound | (curses.A_BOLD if selected == 0 else 0)
            x_sound = (width - len(line_sound)) // 2
            self.stdscr.addstr(y_sound, x_sound, line_sound, attr_sound)

            pointer_back = "▶" if selected == 1 else " "
            line_back = f"{pointer_back} Back"

            color_back = curses.color_pair(2 if (selected == 1 and blink) else 3)
            attr_back = color_back | (curses.A_BOLD if selected == 1 else 0)
            x_back = (width - len(line_back)) // 2
            self.stdscr.addstr(y_back, x_back, line_back, attr_back)
            
            self.stdscr.refresh()

            blink = not blink
            self.stdscr.timeout(300)
            key = self.stdscr.getch()

            if key == -1:
                continue
            if key == curses.KEY_UP:
                selected = (selected - 1) % 2
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % 2
            elif key in (curses.KEY_ENTER, 10, 13):
                if selected == 0:
                    self.sound_on = not self.sound_on
                else:
                    return

    def exit_menu(self) -> bool:
        height, width = self.stdscr.getmaxyx()
        selected = 1
        blink = False

        while True:
            self.stdscr.clear()

            big_block = big_yes if selected == 0 else big_no
            block_h = len(big_block)

            block_top = height // 3 - block_h // 2
            
            for i, line in enumerate(big_block):
                y = block_top + i
                if 0 <= y < height:
                    x = (width - len(line)) // 2
                    self.stdscr.addstr(y, x, line, curses.color_pair(2) | curses.A_BOLD)

            question = "Are you sure you want to leave the game?"
            q_y = block_top + block_h + 2
            q_x = (width - len(question)) // 2
            self.stdscr.addstr(q_y, q_x, question, curses.color_pair(3) | curses.A_BOLD)

            options_local = ["Yes", "No"]
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
                selected = (selected - 1) % 2
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % 2
            elif key in (curses.KEY_ENTER, 10, 13):
                return selected == 0

    def run(self) -> str | None:
        self.stdscr.clear()

        height, width = self.stdscr.getmaxyx()

        logo_top = 1
        logo_height = len(logo)

        menu_height = len(options) + 1

        center_y = height // 2

        menu_top = center_y - menu_height // 2

        animate_logo(self.stdscr, y_offset=logo_top)
        draw_logo(self.stdscr, y_offset=logo_top)

        selected = 0
        blink = False
        
        while True:
            self.stdscr.clear()
            draw_logo(self.stdscr, y_offset=logo_top)
            draw_menu(self.stdscr, first_line_y=menu_top, selected=selected, blink=blink)
            self.stdscr.refresh()
            
            blink = not blink
            self.stdscr.timeout(300)
            key = self.stdscr.getch()

            if key == -1:
                continue
            if key == curses.KEY_UP:
                selected = (selected - 1) % 5
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % 5
            elif key in (curses.KEY_ENTER, 10, 13):
                if selected == 0:
                    self.stdscr.clear()
                    msg = f"The adventure begins. So may God have mercy on your soul, {player_name}!"
                    h, w = self.stdscr.getmaxyx()
                    y = h // 2
                    x = (w - len(msg)) // 2
                    self.stdscr.addstr(y, x, msg, curses.color_pair(3) | curses.A_BOLD)
                    self.stdscr.refresh()
                    self.stdscr.timeout(-1)
                    self.stdscr.getch()
                    return None
                elif selected == 1:
                    slot = self.load_game()
                    if slot is not None:
                        self.stdscr.clear()
                        msg = f"Loading slot <{slot}>!"
                        h, w = self.stdscr.getmaxyx()
                        y = h // 2
                        x = (w - len(msg)) // 2
                        self.stdscr.addstr(y, x, msg, curses.color_pair(3) | curses.A_BOLD)
                        self.stdscr.refresh()
                        self.stdscr.timeout(-1)
                        self.stdscr.getch()
                        return None   
                elif selected == 2:
                    self.score_menu()
                elif selected == 3:
                    self.settings_menu()
                elif selected == 4:
                    if self.exit_menu():
                        self.stdscr.clear()
                        msg = "Good luck! See you next time!"
                        h, w = self.stdscr.getmaxyx()
                        y = h // 2
                        x = (w - len(msg)) // 2
                        self.stdscr.addstr(y, x, msg, curses.color_pair(3) | curses.A_BOLD)
                        self.stdscr.refresh()
                        self.stdscr.timeout(-1)
                        self.stdscr.getch()
                        return None
                    else:
                        continue