import curses

big_logo = [
    r" .--..--..--..--..--..--..--..--..--..--..--..--..--.  ",
    r"/ .. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \ ",
    r"\ \/\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ \/ / ",
    r" \/ /`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'\/ /  ",
    r" / /\                                            / /\  ",
    r"/ /\ \  ____     ___     ____   _   _   _____   / /\ \ ",
    r"\ \/ / |  _ \   / _ \   / ___| | | | | | ____|  \ \/ / ",
    r" \/ /  | |_) | | | | | | |  _  | | | | |  _|     \/ /  ",
    r" / /\  |  _ <  | |_| | | |_| | | |_| | | |___    / /\  ",
    r"/ /\ \ |_| \_\  \___/   \____|  \___/  |_____|  / /\ \ ",
    r"\ \/ /                                          \ \/ / ",
    r" \/ /                                            \/ /  ",
    r" / /\.--..--..--..--..--..--..--..--..--..--..--./ /\  ",
    r"/ /\ \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \.. \/\ \ ",
    r"\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `'\ `' / ",
    r" `--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'`--'  ",
]

big_year = [
    r"███████████████████████████████ ",
    r"█▌ _    ___     ___     ___  ▐█ ",
    r"█▌/ |  / _ \   ( _ )   / _ \ ▐█ ",
    r"█▌| | | (_) |  / _ \  | | | |▐█ ",
    r"█▌| |  \__, | | (_) | | |_| |▐█ ",
    r"█▌|_|    /_/   \___/   \___/ ▐█ ",
    r"███████████████████████████████ ",
]

def loading(stdscr, y_offset: int = 0) -> None:
    height, width = stdscr.getmaxyx()
    big_logo_width = max(len(line) for line in big_logo)

    start_y = y_offset
    start_x = (width - big_logo_width) // 2

    for i, line in enumerate(big_logo):
        y = start_y + i
        if 0 <= y < height:
            stdscr.addstr(y, start_x, line, curses.color_pair(1))
        stdscr.refresh()
        curses.napms(180)

    big_year_width = max(len(line) for line in big_year)
    big_year_y = start_y + len(big_logo) + 2
    big_year_x = max(0, (width - big_year_width) // 2)

    for i, line in enumerate(big_year):
        y = big_year_y + i
        if 0 <= y < height:
            stdscr.addstr(y, big_year_x, line, curses.color_pair(1))
        stdscr.refresh()
        curses.napms(180)

def run_loader(stdscr) -> None:
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)

    loading(stdscr, y_offset=2)

    curses.napms(600)

    stdscr.clear()
    stdscr.refresh()