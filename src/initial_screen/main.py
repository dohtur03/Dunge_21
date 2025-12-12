from menu import *
from game import *
from loader import *
import curses

def main(stdscr):
    game = None
    game_status = "inactive"
    
    run_loader(stdscr)
    
    while True:
        
        menu = Menu(stdscr, game_status)
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
                  
        if result == "quit_game":
            game = None
            game_status = "inactive"  
            break
        
        elif result == "back_to_menu":
            continue
            
if __name__ == "__main__":
    curses.wrapper(main)