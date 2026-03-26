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

                # Зеленая подсказка для главного меню инвентаря
                hint = "<Arrows '↑↓', 'Enter' select, 'q' close>"
                hint_x = max(1, (w - len(hint[:w - 4])) // 2)
                overlay.addstr(h - 2, hint_x, hint[:w - 4], curses.color_pair(4) | curses.A_BOLD)

                overlay.refresh()
                self.stdscr.refresh()

                blink = not blink
                self.stdscr.timeout(300)
                key = self.stdscr.getch()

                # Логика выхода ('q' или Escape)
                if key in (ord('q'), 27):
                    overlay.clear()
                    del overlay
                    self.stdscr.refresh()
                    return

                elif key == curses.KEY_UP:
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
        title = f" 🔒 {category.upper()} 🔒 "
        back_index = 9

        while True:
            game.player.update_effects()
            self.game_view.render(game)

            win.clear()
            win.box()

            title_x = max(1, (w // 2) - (len(title) // 2))
            win.addstr(1, title_x, title[:w - 2], curses.color_pair(2) | curses.A_BOLD)

            start_y = 3
            for idx in range(9):
                item = slots[idx]
                item_label = "<none>" if item is None else str(item)

                equipped_tag = " (equipped)" if (
                        category == "Weapon" and item is not None and item == game.player.current_weapon) else ""

                line = f"{idx + 1}. {item_label}{equipped_tag}".ljust(50)[:w - 4]

                y = start_y + idx
                attr = (curses.color_pair(2 if blink else 3) | curses.A_BOLD) if idx == selected else curses.color_pair(
                    3)
                win.addstr(y, max(1, (w - len(line)) // 2), line, attr)

            back_line = "10. Back".ljust(50)[:w - 4]
            attr = (curses.color_pair(2 if blink else 3) | curses.A_BOLD) if 9 == selected else curses.color_pair(3)
            win.addstr(start_y + 9, max(1, (w - len(back_line)) // 2), back_line, attr)

            # --- ОБНОВЛЕННАЯ ЗЕЛЕНАЯ ПОДСКАЗКА ---
            if category == "Weapon":
                hint = "<'Enter'/'1-9' use, '0' unequip, 'q' back>"
            else:
                hint = "<'Enter'/'1-9' use, '0' drop, 'q' back>"

            hint_x = max(1, (w - len(hint)) // 2)
            win.addstr(h - 2, hint_x, hint[:w - 4], curses.color_pair(4) | curses.A_BOLD)

            win.refresh()
            self.stdscr.refresh()

            blink = not blink
            self.stdscr.timeout(300)
            key = self.stdscr.getch()

            # --- ОБРАБОТКА КЛАВИШ ---

            # Выход ('q' или Escape)
            if key in (ord('q'), 27):
                win.clear()
                win.refresh()
                del win
                return

            # Универсальная логика для '0' (Снять или Выбросить)
            elif key == ord('0'):
                if category == "Weapon":
                    msg = game.unequip_weapon()
                    if msg:
                        game.action_msg = msg
                    win.clear()
                    win.refresh()
                    del win
                    return
                else:
                    msg = game.drop_item(category, selected)
                    if msg:
                        game.action_msg = msg

            # --- НОВАЯ ЛОГИКА: Быстрое применение на 1-9 ---
            elif ord('1') <= key <= ord('9'):
                slot_idx = key - ord('1')  # '1' -> 0, '2' -> 1 и т.д.
                msg = game.use_item(category, slot_idx)
                if msg:
                    game.action_msg = msg
            # -----------------------------------------------

            elif key == curses.KEY_UP:
                selected = (selected - 1) % 10
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % 10
            elif key in (curses.KEY_ENTER, 10, 13):
                if selected == back_index:
                    win.clear()
                    win.refresh()
                    del win
                    return

                msg = game.use_item(category, selected)
                if msg:
                    game.action_msg = msg

            elif key == curses.KEY_UP:
                selected = (selected - 1) % 10
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % 10
            elif key in (curses.KEY_ENTER, 10, 13):
                if selected == back_index:
                    win.clear()
                    win.refresh()
                    del win
                    return

                msg = game.use_item(category, selected)
                if msg:
                    game.action_msg = msg

    def show_classic_inventory(self, game, category: str):
        """Олдскульный инвентарь по ТЗ: выбор кнопками 1-9 (и 0 для снятия оружия)"""
        height, width = self.stdscr.getmaxyx()
        h, w = 16, 60
        h = min(h, height - 2)
        w = min(w, width - 2)
        win_y = max(1, (height - h) // 2)
        win_x = max(1, (width - w) // 2)

        win = curses.newwin(h, w, win_y, win_x)
        win.bkgdset(' ', curses.color_pair(8) | curses.A_BOLD)

        slots = game.player.inventory.category_items.get(category, [])
        title = f" 🔒 {category.upper()} 🔒 "

        while True:
            self.game_view.render(game)

            win.clear()
            win.box()

            title_x = max(1, (w // 2) - (len(title) // 2))
            win.addstr(1, title_x, title[:w - 2], curses.color_pair(2) | curses.A_BOLD)

            start_y = 3
            for idx in range(9):
                item = slots[idx] if idx < len(slots) else None
                item_label = "<empty>" if item is None else str(item)

                equipped_tag = " (equipped)" if (
                        category == "Weapon" and item is not None and item == game.player.current_weapon) else ""

                line = f"{idx + 1}. {item_label}{equipped_tag}"
                win.addstr(start_y + idx, 3, line[:w - 4], curses.color_pair(3))

            prompt_y = start_y + 10
            if category == "Weapon":
                win.addstr(prompt_y, 3, "0. Unequip weapon", curses.color_pair(4) | curses.A_BOLD)

            prompt_msg = f"Choose item (1-9)"
            if category == "Weapon":
                prompt_msg += ", '0' to unequip"
            prompt_msg += " or 'q' to cancel:"

            win.addstr(prompt_y + 1, 3, prompt_msg[:w - 4], curses.color_pair(4) | curses.A_BOLD)

            win.refresh()
            self.stdscr.refresh()

            self.stdscr.timeout(-1)
            key = self.stdscr.getch()

            if key in (ord('q'), 27):
                win.clear()
                del win
                return

            if category == "Weapon" and key == ord('0'):
                msg = game.unequip_weapon()
                if msg:
                    game.action_msg = msg
                win.clear()
                del win
                return

            if ord('1') <= key <= ord('9'):
                slot_idx = key - ord('1')
                msg = game.use_item(category, slot_idx)
                if msg:
                    game.action_msg = msg

                win.clear()
                del win
                return