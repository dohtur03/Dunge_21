import curses

class Game:
    def __init__(self, stdscr, player_name: str):
        self.stdscr = stdscr
        self.player_name = player_name

    @classmethod
    def from_slot(cls, stdscr, slot_name: str):
        game = cls(stdscr, f"Player_{slot_name}")
        return game

    def run(self) -> None:
        while True:
            self.stdscr.clear()
            
            height, width = self.stdscr.getmaxyx()
            msg = f"Game started for {self.player_name}!"
            y_msg = 2
            x_msg = (width - len(msg)) // 2
            self.stdscr.addstr(y_msg, x_msg, msg, curses.color_pair(4) | curses.A_BOLD)

            hint = "Press 'q' to quit!"
            y_hint = y_msg + 2
            x_hint = (width - len(hint)) // 2
            self.stdscr.addstr(y_hint, x_hint, hint, curses.color_pair(3))

            self.stdscr.refresh()
            
            self.stdscr.timeout(-1)
            key = self.stdscr.getch()
            
            if key == ord('q'):
                break