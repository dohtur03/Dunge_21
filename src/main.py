import curses
import time
from presentation.menu import Menu
from domain.game import Game
from presentation.game_view import GameView
from presentation.loader import run_loader
from datalayer.score import save_score
from presentation.log import death_message, get_random_message
from presentation.inventory_view import InventoryView


def run_game_loop(stdscr, game, view):
    """Контроллер игрового цикла (Controller)"""
    while True:
        # 1. Отрисовываем текущее состояние (View)
        view.render(game)

        # 2. Проверяем, нужно ли показать случайный попап
        current_time = time.time()
        if view.logger.needs_popup(current_time):
            msg = get_random_message()
            view.logger.show_popup(stdscr, msg)
            view.logger.last_popup = current_time

        # 3. Ждем нажатия клавиши от пользователя
        stdscr.timeout(100)
        key = stdscr.getch()

        if key == -1:
            continue

        # 4. Передаем клавишу в бизнес-логику для пересчета (Model)
        action = game.process_turn(key)

        # 5. Обрабатываем результаты хода
        if action == "died":
            view.logger.show_popup(stdscr, death_message)
            return "quit_game"

        elif action == "request_quit":
            option = view.show_exit_menu()
            if option == 0:  # Yes
                stdscr.clear()
                msg = "Good luck! See you next time!"
                h, w = stdscr.getmaxyx()
                stdscr.addstr(h // 2, (w - len(msg)) // 2, msg, curses.color_pair(3) | curses.A_BOLD)
                stdscr.refresh()
                stdscr.timeout(-1)
                stdscr.getch()
                return "quit_game"
            elif option == 1:  # No
                continue
            elif option == 2:  # Back to menu
                return "back_to_menu"

        elif action == "open_inventory":
            inv_view = InventoryView(stdscr, view)
            inv_view.show(game)


def main(stdscr):
    game = None
    game_status = "inactive"

    run_loader(stdscr)

    while True:
        menu = Menu(stdscr, game_status, player_name=getattr(game, 'player_name', '<default_player>'))
        action, data = menu.run()

        if action == "new_game":
            game = Game(data)
            view = GameView(stdscr)
            # Передаем управление в контроллер
            result = run_game_loop(stdscr, game, view)
            game_status = "active"

        elif action == "load_game":
            slot_index = data
            game_data = menu.storage.load_slot(slot_index)
            if game_data is not None:
                game_data.pop("__slot_index__", None)
                game = Game.from_dict(game_data)
                view = GameView(stdscr)
                result = run_game_loop(stdscr, game, view)
                game_status = "active"
            else:
                msg = "No save file in this slot!"
                h, w = stdscr.getmaxyx()
                stdscr.clear()
                stdscr.addstr(h // 2, (w - len(msg)) // 2, msg, curses.color_pair(1) | curses.A_BOLD)
                stdscr.refresh()
                stdscr.timeout(1500)
                stdscr.getch()
            continue

        elif action == "save_game":
            if game is not None:
                slot_index = data
                game_data = game.save_game_data_to_dict()
                game_data["__slot_index__"] = slot_index
                success = menu.storage.save_slot(slot_index, game_data)

                msg = f"Saved to slot {slot_index}!" if success else "Save failed!"
                h, w = stdscr.getmaxyx()
                stdscr.clear()
                stdscr.addstr(h // 2, (w - len(msg)) // 2, msg, curses.color_pair(4) | curses.A_BOLD)
                stdscr.refresh()
                stdscr.timeout(1500)
                stdscr.getch()
            continue

        elif action == "back_to_game":
            if game is not None:
                view = GameView(stdscr)
                result = run_game_loop(stdscr, game, view)
            else:
                result = None

        else:
            result = "quit_game"

        if result == "quit_game":
            if game is not None:
                real_score = game.get_score()
                save_score(game.player_name, real_score)
                h, w = stdscr.getmaxyx()
                stdscr.clear()
                stdscr.addstr(h // 2, (w - 30) // 2, f"Saved: {game.player_name} - {real_score} points",
                              curses.color_pair(4) | curses.A_BOLD)
                stdscr.refresh()
                stdscr.timeout(-1)
                stdscr.getch()
            break

        elif result == "back_to_menu":
            continue

        if __name__ == "__main__":
            curses.wrapper(main)


if __name__ == "__main__":
    curses.wrapper(main)