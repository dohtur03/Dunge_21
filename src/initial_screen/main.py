from menu import Menu
from game import Game
import curses

def main(stdscr):
    menu = Menu(stdscr)
    action, data = menu.run()

    if action == "new_game":
        game = Game(stdscr, data)
        game.run()
    elif action == "load_game":
        game = Game.from_slot(stdscr, data)
        game.run()

if __name__ == "__main__":
    curses.wrapper(main)