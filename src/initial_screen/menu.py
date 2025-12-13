import curses
from draw import *

class Menu():
    def __init__(self, stdscr, game_status: str = "inactive", player_name: str = "<default_player>"):
        self.stdscr = stdscr
        self.stdscr.keypad(True)
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
        self.player_name = player_name

        self.has_active_game = (game_status == "active")
    
    def get_player_name(self) -> str:
        height, width = self.stdscr.getmaxyx()
        max_name_len = 20

        while True:
            self.stdscr.clear()

            big_block = big_start
            block_h = len(big_block)
            y_title_block = height // 4 - block_h // 2

            for i, line in enumerate(big_block):
                y = y_title_block + i
                if 0 <= y < height:
                    x = (width - len(line)) // 2
                    self.stdscr.addstr(y, x, line, curses.color_pair(2) | curses.A_BOLD)

            title = "Enter your name:"
            hint = "<Type your name and press 'Enter' to start ('Backspace' to delete char)>"

            y_title = height // 2
            x_title = (width - len(title)) // 2
            self.stdscr.addstr(y_title, x_title, title, curses.color_pair(2) | curses.A_BOLD)

            y_hint = y_title + 2
            x_hint = (width - len(hint)) // 2
            self.stdscr.addstr(y_hint, x_hint, hint, curses.color_pair(3))

            y_input = y_hint + 2
            x_input = (width - max_name_len - 2) // 2
        
            name_buffer = ""
            curses.noecho()
            curses.curs_set(2)
        
            while True:
                self.stdscr.move(y_input, x_input + 1)
                self.stdscr.clrtoeol()
            
                if name_buffer:
                    self.stdscr.addstr(y_input, x_input + 1, name_buffer, curses.color_pair(4))
            
                self.stdscr.move(y_input, x_input + 1 + len(name_buffer))
                self.stdscr.refresh()

                key = self.stdscr.getch()

                if key in (10, 13, curses.KEY_ENTER):
                    curses.curs_set(0)
                    name = name_buffer.strip()
                    break
                
                elif key in (127, 8, curses.KEY_BACKSPACE):
                    name_buffer = name_buffer[:-1]
                
                elif 32 <= key <= 126 and len(name_buffer) < max_name_len:
                    name_buffer += chr(key)

            if not name:
                self.stdscr.clear()
                name_msg = "Please enter your name to start!!"
                h, w = self.stdscr.getmaxyx()
                msg_y = h // 2
                msg_x = (w - len(name_msg)) // 2
                self.stdscr.addstr(msg_y, msg_x, name_msg, curses.color_pair(1) | curses.A_BOLD)
                self.stdscr.refresh()
                self.stdscr.timeout(-1)
                self.stdscr.getch()
                curses.curs_set(0)
                continue

            self.player_name = name
            curses.curs_set(0)
            return name

    def load_game(self) -> str | None:
        selected = 0
        blink = False

        slots = ["<test_slot>"] + ["<empty>"] * 9 + ["Back"]
        back_index = len(slots) - 1

        while True:
            height, width = self.stdscr.getmaxyx()
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
        
        while True:
            self.stdscr.clear()
            draw_score(self.stdscr, height, width)
            self.stdscr.refresh()
            self.stdscr.timeout(-1)
            key = self.stdscr.getch()
            break
    
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

            question = "Are you sure you want to exit?"
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

    def save_game(self) -> None:
        self.stdscr.clear()
        msg = f"Game saved successfully, {self.player_name}!"
        h, w = self.stdscr.getmaxyx()
        y = h // 2
        x = (w - len(msg)) // 2
        self.stdscr.addstr(y, x, msg, curses.color_pair(4) | curses.A_BOLD)
        self.stdscr.refresh()
        self.stdscr.timeout(-1)
        self.stdscr.getch()

    def run(self) -> tuple[str, str | None]:
        height, width = self.stdscr.getmaxyx()
        logo_top = 1
        center_y = height // 2
        menu_top = center_y - (how_many_options + 1) // 2

        selected = 0
        blink = False

        total_items = how_many_options + 2 if self.has_active_game else how_many_options
        base_index_offset = 2 if self.has_active_game else 0

        while True:
            self.stdscr.clear()
            draw_logo(self.stdscr, y_offset=logo_top)
            draw_menu_items(self.stdscr, menu_top, total_items, selected, blink, self.has_active_game, base_index_offset, width)

            menu_index = selected - base_index_offset if not (self.has_active_game and selected in (0, 1)) else -1
            big_block = get_big_block(menu_index, self.has_active_game, selected)
            draw_big_block(self.stdscr, big_block, width, height)
            draw_bottom_panel(self.stdscr, height, width)
        
            self.stdscr.refresh()
            blink = not blink
            self.stdscr.timeout(300)
            key = self.stdscr.getch()
        
            if key == -1: 
                continue
            if key == curses.KEY_UP: 
                selected = (selected - 1) % total_items
            elif key == curses.KEY_DOWN: 
                selected = (selected + 1) % total_items
            elif key in (curses.KEY_ENTER, 10, 13):
                if self.has_active_game and selected == 0:
                    return ("back_to_game", None)
                elif self.has_active_game and selected == 1:
                    self.save_game()
                    continue
                
                index = selected - base_index_offset
                if index == 0:
                    self.get_player_name()
                    self.stdscr.clear()
                    msg = f"The adventure begins. So may God have mercy on your soul, {self.player_name}!"
                    h, w = self.stdscr.getmaxyx()
                    y = h // 2
                    x = (w - len(msg)) // 2
                    self.stdscr.addstr(y, x, msg, curses.color_pair(3) | curses.A_BOLD)
                    self.stdscr.refresh()
                    self.stdscr.timeout(-1)
                    self.stdscr.getch()
                    return ("new_game", self.player_name)
                elif index == 1:
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
                        return ("load_game", slot) 
                elif index == 2:
                    self.score_menu()
                elif index == 3:
                    self.settings_menu()
                elif index == 4:
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
                        return ("exit", None)
                    else:
                        continue