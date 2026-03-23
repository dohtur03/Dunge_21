import curses
import time


class InventoryView:
    def __init__(self, stdscr, game_view):
        self.stdscr = stdscr
        self.game_view = game_view

    def show(self, game):
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
                game.player.update_effects()
                game.player_score = int(time.time() - game.start_time)

                # Перерисовываем игру на фоне
                self.game_view.render(game)

                overlay.clear()
                overlay.box()

                title = "🔒 INVENTORY 🔒"
                title_x = max(1, (w // 2) - (len(title) // 2))
                overlay.addstr(1, title_x, title, curses.color_pair(2) | curses.A_BOLD)

                pointer = "▶"
                start_y = 3
                for i, category in enumerate(game.player.inventory.categories):
                    y = start_y + i
                    line = f"{pointer} {category}" if i == selected else f"  {category}"
                    attr = (curses.color_pair(
                        2 if blink else 3) | curses.A_BOLD) if i == selected else curses.color_pair(3)

                    if len(line) > w - 4:
                        line = line[: w - 4]
                    line_x = (w - len(line)) // 2
                    overlay.addstr(y, line_x, line, attr)

                hint = "<Arrows '↑↓' to choose, 'Enter' to select>"
                hint_x = (w - len(hint[:w - 4])) // 2
                overlay.addstr(h - 2, hint_x, hint[:w - 4], curses.color_pair(3))

                overlay.refresh()
                self.stdscr.refresh()

                blink = not blink
                self.stdscr.timeout(300)
                key = self.stdscr.getch()

                if key == curses.KEY_UP:
                    selected = (selected - 1) % len(game.player.inventory.categories)
                elif key == curses.KEY_DOWN:
                    selected = (selected + 1) % len(game.player.inventory.categories)
                elif key in (curses.KEY_ENTER, 10, 13):
                    selected_category = game.player.inventory.categories[selected]

                    if selected_category == "Back":
                        overlay.clear()
                        del overlay
                        self.stdscr.refresh()
                        return

                    self.show_category_items(game, selected_category)

                    overlay.clear()
                    del overlay
                    self.stdscr.refresh()
                    break

    def show_category_items(self, game, category: str):
        height, width = self.stdscr.getmaxyx()
        h, w = 15, 80
        h = min(h, height - 2)
        w = min(w, width - 2)
        win_y = max(1, (height - h) // 2)
        win_x = max(1, (width - w) // 2)

        win = curses.newwin(h, w, win_y, win_x)
        win.bkgdset(' ', curses.color_pair(8) | curses.A_BOLD)

        slots = game.player.inventory.category_items[category]
        selected = 0
        blink = False
        title = f"   🔒 {category.upper()} 🔒"
        back_index = 9

        while True:
            game.player.update_effects()
            game.player_score = int(time.time() - game.start_time)
            self.game_view.render(game)

            win.clear()
            win.box()

            title_x = max(1, (w // 2) - (len(title) // 2) - 1)
            win.addstr(1, title_x, title[:w - 2], curses.color_pair(2) | curses.A_BOLD)

            start_y = 3
            for idx in range(9):
                item = slots[idx]
                item_label = "<none>" if item is None else str(item)

                # ИСПРАВЛЕННАЯ СТРОКА: добавлено item is not None
                equipped_tag = " (equipped)" if (
                            category == "Weapon" and item is not None and item == game.player.current_weapon) else ""

                line = f"{idx + 1}. {item_label}{equipped_tag}".ljust(50)[:w - 4]

                y = start_y + idx
                attr = (curses.color_pair(2 if blink else 3) | curses.A_BOLD) if idx == selected else curses.color_pair(
                    3)
                win.addstr(y, (w - len(line)) // 2, line, attr)

            back_line = "10. Back".ljust(50)[:w - 4]
            attr = (curses.color_pair(2 if blink else 3) | curses.A_BOLD) if 9 == selected else curses.color_pair(3)
            win.addstr(start_y + 9, (w - len(back_line)) // 2, back_line, attr)

            hint = "<Arrows '↑↓' to choose, 'Enter' to select, 'Delete' to pick off>"
            win.addstr(h - 2, (w - len(hint[:w - 4])) // 2, hint[:w - 4], curses.color_pair(3))

            win.refresh()
            self.stdscr.refresh()

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
                    return

                # Передаем команду "использовать" в бизнес-логику
                msg = game.use_item(category, selected)
                if msg:
                    self.game_view.logger.show_popup(self.stdscr, msg)

            elif key == curses.KEY_DC:  # Delete
                # Передаем команду "выбросить" в бизнес-логику
                msg = game.drop_item(category, selected)
                if msg:
                    self.game_view.logger.show_popup(self.stdscr, msg)