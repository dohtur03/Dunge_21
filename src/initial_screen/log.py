import time
import random
from typing import List
import curses

test_messages = [
    "Great! You're still alive! Big balls!",
    "Keep trying! Never give up!",
    "Just do your best to survive!",
    "10 seconds alive! Unreal!",
    "You're good enough to survive 10 seconds...",
    "Are you still here? Cool!",
]

death_message = "You died!"

def get_random_message() -> str:
    return random.choice(test_messages)

class GameLog:
    def __init__(self):
        self.last_popup = time.time()
        self.popup_interval = 10
    
    def needs_popup(self, current_time: float) -> bool:
        return (current_time - self.last_popup) >= self.popup_interval

    def show_popup(self, stdscr, message: str) -> None:
        height, width = stdscr.getmaxyx()
        h, w = 7, 50

        win_y = max(1, (height - h) // 2)
        win_x = max(1, (width - w) // 2)

        overlay = curses.newwin(h, w, win_y, win_x)
        overlay.bkgdset(' ', curses.color_pair(8) | curses.A_BOLD)
        overlay.box()

        title = "🎮 STATUS UPDATE 🎮"
        title_x = (w - len(title)) // 2
        overlay.addstr(1, title_x, title, curses.color_pair(2) | curses.A_BOLD)

        msg_lines = [message[i:i+w-6] for i in range(0, len(message), w-6)]
        for i, line in enumerate(msg_lines[:2]):
            line_x = (w - len(line)) // 2
            overlay.addstr(2 + i, line_x, line[:w-4], curses.color_pair(4) | curses.A_BOLD)

        bottom = "Press any key to continue..."
        bottom_x = (w - len(bottom)) // 2
        overlay.addstr(5, bottom_x, bottom, curses.color_pair(3))
        
        overlay.refresh()
        
        start_time = time.time()
        timeout_duration = 2000
        
        while True:
            stdscr.timeout(timeout_duration)
            key = stdscr.getch()
        
            elapsed = (time.time() - start_time) * 1000
            remaining = max(0, timeout_duration - elapsed)
        
            stdscr.timeout(int(remaining))
        
            if key != -1 or elapsed >= 2000:
                break

        overlay.clear()
        del overlay
        stdscr.refresh()