from menu import *
import curses


def main(stdscr):
    menu = Menu(stdscr)
    player_name = menu.run()

if __name__ == "__main__":
    curses.wrapper(main)