import curses
from menu import *
from game import *
from loader import *
from score import *

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
            game = Game.from_slot(stdscr, data)
            result = game.run()
            game_status = "active"

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