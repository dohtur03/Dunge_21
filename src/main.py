from datalayer.score import save_score
from presentation.menu import *
from domain.game import *
from presentation.loader import *


def main(stdscr):
    game = None
    game_status = "inactive"
    
    run_loader(stdscr)
    
    while True:
        menu = Menu(stdscr, game_status, player_name=getattr(game, 'player_name', '<default_player>'))
        action, data = menu.run()

        if action == "new_game":
            game = Game(stdscr, data)
            result = game.run()
            game_status = "active"
        
        elif action == "load_game":
            slot_index = data
            game_data = menu.storage.load_slot(slot_index)
            if game_data is not None:
                game_data.pop("__slot_index__", None)  
                game = Game.from_dict(stdscr, game_data)
                result = game.run()
                game_status = "active"
            else:
                msg = "No save file in this slot!"
                h, w = stdscr.getmaxyx()
                y, x = h // 2, (w - len(msg)) // 2
                stdscr.clear()
                stdscr.addstr(y, x, msg, curses.color_pair(1) | curses.A_BOLD)
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
                height, width = stdscr.getmaxyx()
                y = height // 2
                x = (width - len(msg)) // 2
                stdscr.clear()
                stdscr.addstr(y, x, msg, curses.color_pair(4) | curses.A_BOLD)
                stdscr.refresh()
                stdscr.timeout(1500)
                stdscr.getch()
            continue

        elif action == "back_to_game":
            if game is not None:
                result = game.run()
            else:
                result = None
        
        else:
            result = "quit_game"

        if result == "quit_game" and game is not None:
            real_score = game.get_score()
            save_score(game.player_name, real_score)
            height, width = stdscr.getmaxyx()
            msg_y = height // 2
            msg_x = (width - 30) // 2
            stdscr.clear()
            stdscr.addstr(msg_y, msg_x, f"Saved: {game.player_name} - {real_score} points", curses.color_pair(4) | curses.A_BOLD)
            stdscr.refresh()
            stdscr.timeout(-1)
            stdscr.getch()
        if result == "quit_game":
            game = None
            game_status = "inactive"  
            break
        
        elif result == "back_to_menu":
            continue
            
if __name__ == "__main__":
    curses.wrapper(main)