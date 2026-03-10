import curses
from domain.item import *
import time

class Inventory:
    def __init__(self, stdscr, player_name: str, game):
        self.stdscr = stdscr
        self.player_name = player_name
        self.game = game
        self.categories = ["Weapon", "Food", "Potion", "Scroll", "Back"]
        self.category_items = {
            "Weapon": [None] * 9,
            "Food":   [None] * 9,
            "Potion": [None] * 9,
            "Scroll": [None] * 9,
        }
    
    def to_dict(self) -> dict:
        result = {}
        for category, items in self.category_items.items():
            result[category] = [
                item.to_dict() if item is not None else None
                for item in items
            ]
        return result
    
    @classmethod
    def from_dict(cls, stdscr, player_name, game, data: dict) -> "Inventory":
        inv = cls(stdscr, player_name, game)
        for category, item_list in data.items():
            if category in inv.category_items:
                inv.category_items[category] = [
                    Item.from_dict(item_data) if item_data is not None else None
                    for item_data in item_list
                ]
        return inv

    def show(self) -> str | None:
        height, width = self.stdscr.getmaxyx()
        h, w = 15, 60
        h = min(h, height - 2)
        w = min(w, width - 2)
        win_y = max(1, (height - h) // 2)
        win_x = max(1, (width - w) // 2)

        while True:
            overlay = curses.newwin(h, w, win_y, win_x)
            overlay.bkgdset(' ', curses.color_pair(8) | curses.A_BOLD)
            selected = 0
            blink = False
        
            while True:
                self.game.update_effects()
                self.game.player_score = int(time.time() - self.game.start_time)
                
                height, width = self.game.stdscr.getmaxyx()
                self.game.draw_panel(height, width)
                self.game.draw_bottom_panel(height, width)

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
                self.game.stdscr.refresh()

                blink = not blink
                self.stdscr.timeout(300)
                key = self.stdscr.getch()

                if key == curses.KEY_UP:
                    selected = (selected - 1) % len(self.categories)
                elif key == curses.KEY_DOWN:
                    selected = (selected + 1) % len(self.categories)
                elif key in (curses.KEY_ENTER, 10, 13):
                    selected_category = self.categories[selected]
                    
                    if selected_category == "Back":
                        overlay.clear()
                        del overlay
                        self.stdscr.refresh()
                        return None
                
                    result = self.show_category_items(selected_category)
                    overlay.clear()
                    del overlay
                    self.stdscr.refresh()
                    
                    if result != "Back":
                        return selected_category
                    break

    def show_category_items(self, category: str) -> str | None:
        height, width = self.stdscr.getmaxyx()
        h, w = 15, 80

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
            self.game.update_effects()
            self.game.player_score = int(time.time() - self.game.start_time)
            
            height, width = self.game.stdscr.getmaxyx()
            self.game.draw_panel(height, width)
            self.game.draw_bottom_panel(height, width)

            win.clear()
            win.box()

            title_x = (w // 2) - (len(title) // 2) - 1
            if title_x < 1:
                title_x = 1
            win.addstr(1, title_x, title, curses.color_pair(2) | curses.A_BOLD)

            start_y = 3
            fixed_line_width = 50

            max_line_len = fixed_line_width
            lines = []
            
            for idx in range(9):
                item = slots[idx]
                
                if item is None:
                    item_label = "<none>"
                else:
                    item_label = str(item)
                
                
                equipped_tag = " (equipped)" if (category == "Weapon" and item == self.game.current_weapon) else ""

                label = f"{item_label}{equipped_tag}"
                line = f"{idx + 1}. {label}"
                
                line = line[:fixed_line_width].ljust(fixed_line_width)
                lines.append(line)
            
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

            back_line = "10. Back"
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

            hint = "<Arrows '↑↓' to choose, 'Enter' to select, 'Delete' to pick off>"
            if len(hint) > w - 4:
                hint = hint[: w - 4]
            hint_x = (w - len(hint)) // 2
            win.addstr(h - 2, hint_x, hint, curses.color_pair(3))

            win.refresh()
            self.game.stdscr.refresh()

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
                    return "Back"

                slot_idx = selected
                item = slots[slot_idx]

                if item is None:
                    continue
                
                if category == "Weapon":
                    if self.game.current_weapon is item:
                        self.game.current_weapon = None
                        msg = f"{item.name} unequipped"
                    else:
                        self.game.current_weapon = item
                        msg = f"{item.name} equipped"
                    
                    self.game.logger.show_popup(self.game.stdscr, msg)
                    height, width = self.game.stdscr.getmaxyx()
                    self.game.draw_panel(height, width)
                    self.game.draw_bottom_panel(height, width)
                    self.game.stdscr.refresh()
                    self.game.update_stats()
                    continue
                if category == "Food":
                    old_hits = self.game.player_hits
                    if old_hits == self.game.player_max_hits:
                        msg = "HP full!"
                    else:    
                        self.game.player_hits += item.value
                        msg = f"Eaten {item.name}! Restored {item.value} HP!"

                        if self.game.player_hits >= self.game.player_max_hits:
                            msg = f"Eaten {item.name}! Restored {self.game.player_max_hits - old_hits} HP!"
                            self.game.player_hits = self.game.player_max_hits
                    self.game.logger.show_popup(self.stdscr, msg)
                    height, width = self.game.stdscr.getmaxyx()
                    self.game.draw_panel(height, width)
                    self.game.draw_bottom_panel(height, width)
                    self.game.stdscr.refresh()
                    slots[slot_idx] = None
                    continue
                if category == "Scroll":
                    if item.effect_type == "max_hits":
                        self.game.player_max_hits += item.value
                        self.game.player_hits += item.value
                        msg = f"{item.name} is used! MAX HP and current HP increased by {item.value}!"
                    elif item.effect_type == "agility":
                        self.game.player_agility += item.value
                        msg = f"{item.name} is used! Agility increased by {item.value}!" 
                    elif item.effect_type == "strength":
                        self.game.player_str += item.value
                        msg = f"{item.name} is used! Strength increased by {item.value}!"
                    self.game.logger.show_popup(self.game.stdscr, msg)
                    height, width = self.game.stdscr.getmaxyx()
                    self.game.draw_panel(height, width)
                    self.game.draw_bottom_panel(height, width)
                    self.game.stdscr.refresh()
                    slots[slot_idx] = None
                    continue
                if category == "Potion":
                    effect_duration = item.effect_duration * 60
                    if item.effect_type == "max_hits":
                        self.game.add_potion_effect("max_hits", item.value, effect_duration)
                        msg = f"{item.name} is used! MAX HP +{item.value} for {item.effect_duration} min!"
                    elif item.effect_type == "agility":
                        self.game.add_potion_effect("agility", item.value, effect_duration)
                        msg = f"{item.name} is used! Agility increased by {item.value} for {item.effect_duration} min!"
                    elif item.effect_type == "strength":
                        self.game.add_potion_effect("strength", item.value, effect_duration)
                        msg = f"{item.name} is used! Strength increased by {item.value} for {item.effect_duration} min!"
                    self.game.logger.show_popup(self.game.stdscr, msg)
                    height, width = self.game.stdscr.getmaxyx()
                    self.game.draw_panel(height, width)
                    self.game.draw_bottom_panel(height, width)
                    self.game.stdscr.refresh()
                    slots[slot_idx] = None
                    continue
                else:
                    win.clear()
                    win.refresh()
                    del win
                    return (category, slot_idx, item)
            elif key == curses.KEY_DC:
                slot_idx = selected
                item = slots[slot_idx]
    
                if item is None:
                    continue
    
                slots[slot_idx] = None

                if category == "Weapon" and item == self.game.current_weapon:
                    self.game.current_weapon = None
                
                msg = f"Thrown away: {item.name}"
                self.game.logger.show_popup(self.game.stdscr, msg)
                continue