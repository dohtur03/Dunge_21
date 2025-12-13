import curses

class Inventory:
    def __init__(self, stdscr, player_name: str):
        self.stdscr = stdscr
        self.player_name = player_name
        self.categories = ["Weapon", "Food", "Potion", "Scroll", "Back"]
        self.category_items = {
            "Weapon": [None] * 9,
            "Food":   [None] * 9,
            "Potion": [None] * 9,
            "Scroll": [None] * 9,
        }
    
    def show(self) -> str | None:
        height, width = self.stdscr.getmaxyx()
        h, w = 15, 60

        h = min(h, height - 2)
        w = min(w, width - 2)

        win_y = max(1, (height - h) // 2)
        win_x = max(1, (width - w) // 2)

        overlay = curses.newwin(h, w, win_y, win_x)
        overlay.bkgdset(' ', curses.color_pair(8) | curses.A_BOLD)

        selected = 0
        blink = False

        while True:
            overlay.clear()
            overlay.box()

            title = "🔒 INVENTORY 🔒"
            title = title.strip()
            if len(title) > w - 2:
                title = title[: w - 2]
            
            title_len = len(title)
            title_x = (w // 2) - (title_len // 2)
            title_x = max(1, title_x)
            overlay.addstr(1, title_x, title, curses.color_pair(2) | curses.A_BOLD)

            pointer = "▶"
            start_y = 3
            for i, category in enumerate(self.categories):
                y = start_y + i
                if i == selected:
                    line = f"{pointer} {category}"
                    attr = curses.color_pair(2 if blink else 3) | curses.A_BOLD
                else:
                    line = f"  {category}"
                    attr = curses.color_pair(3)

                if len(line) > w - 4:
                    line = line[: w - 4]
                line_x = (w - len(line)) // 2
                overlay.addstr(y, line_x, line, attr)

            hint = "<Arrows '↑↓' to choose, 'Enter' to select>"
            if len(hint) > w - 4:
                hint = hint[: w - 4]
            hint_x = (w - len(hint)) // 2
            overlay.addstr(h - 2, hint_x, hint, curses.color_pair(3))

            overlay.refresh()

            blink = not blink
            self.stdscr.timeout(300)
            key = self.stdscr.getch()

            if key == curses.KEY_UP:
                selected = (selected - 1) % len(self.categories)
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % len(self.categories)
            elif key in (curses.KEY_ENTER, 10, 13):
                selected_category = self.categories[selected]
                overlay.clear()
                del overlay
                self.stdscr.refresh()

                if selected_category == "Back":
                    return None
                return selected_category

    def show_category_items(self, category: str) -> str | None:
        height, width = self.stdscr.getmaxyx()
        h, w = 15, 60

        h = min(h, height - 2)
        w = min(w, width - 2)

        win_y = max(1, (height - h) // 2)
        win_x = max(1, (width - w) // 2)

        win = curses.newwin(h, w, win_y, win_x)
        win.bkgdset(' ', curses.color_pair(8) | curses.A_BOLD)

        slots = self.category_items[category]

        selected = 0
        blink = False

        title = f"   🔒 {category.upper()} 🔒"
        if len(title) > w - 2:
            title = title[: w - 2]

        back_index = 9
        
        while True:
            win.clear()
            win.box()

            title_x = (w // 2) - (len(title) // 2) - 1
            if title_x < 1:
                title_x = 1
            win.addstr(1, title_x, title, curses.color_pair(2) | curses.A_BOLD)

            start_y = 3

            max_line_len = 0
            lines = []

            for idx in range(9):
                item = slots[idx]
                label = "<none>" if item is None else str(item)
                line = f"{idx + 1}. {label}"
                if len(line) > w - 4:
                    line = line[: w - 4]
                lines.append(line)
                max_line_len = max(max_line_len, len(line))

            for idx, line in enumerate(lines):
                y = start_y + idx
                padded_line = line.ljust(max_line_len)
                if len(padded_line) > w - 4:
                    padded_line = padded_line[: w - 4]

                if idx == selected:
                    attr = curses.color_pair(2 if blink else 3) | curses.A_BOLD
                else:
                    attr = curses.color_pair(3)

                x = (w - len(padded_line)) // 2
                win.addstr(y, x, padded_line, attr)

            back_line = "10. Close"
            if len(back_line) > w - 4:
                back_line = back_line[: w - 4]
                
            padded_back_line = back_line.ljust(max_line_len)
            if len(padded_back_line) > w - 4:
                padded_back_line = padded_back_line[: w - 4]

            y = start_y + 9
            if 9 == selected:
                attr = curses.color_pair(2 if blink else 3) | curses.A_BOLD
            else:
                attr = curses.color_pair(3)

            x = (w - len(padded_back_line)) // 2
            win.addstr(y, x, padded_back_line, attr)

            hint = "<Arrows '↑↓' to choose, 'Enter' to select>"
            if len(hint) > w - 4:
                hint = hint[: w - 4]
            hint_x = (w - len(hint)) // 2
            win.addstr(h - 2, hint_x, hint, curses.color_pair(3))

            win.refresh()

            blink = not blink
            self.stdscr.timeout(300)
            key = self.stdscr.getch()

            if key == curses.KEY_UP:
                selected = (selected - 1) % 10
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % 10
            elif key in (curses.KEY_ENTER, 10, 13):
                if selected == back_index:
                    win.clear()
                    win.refresh()
                    del win
                    return None

                slot_idx = selected
                item = slots[slot_idx]

                if item is None:
                    continue

                chosen = f"{category} slot {slot_idx + 1}: {item}"
                win.clear()
                win.refresh()
                del win
                return (category, slot_idx, item)